from __future__ import annotations

import importlib


def _needs_gemma4_e2b_compat(config) -> bool:
    return (
        getattr(config, "model_type", None) == "gemma4_text"
        and getattr(config, "hidden_size", None) == 1536
        and getattr(config, "num_hidden_layers", None) == 35
        and getattr(config, "num_kv_shared_layers", 0) > 0
    )


def apply_patch() -> None:
    try:
        module = importlib.import_module("mlx_lm.models.gemma4_text")
        nn = importlib.import_module("mlx.nn")
    except Exception:
        return

    if getattr(module, "_finetune_lab_gemma4_e2b_compat_applied", False):
        return

    original_attention_init = module.Attention.__init__
    original_text_model_init = module.Gemma4TextModel.__init__
    original_make_cache = module.Model.make_cache

    def patched_attention_init(self, config, layer_idx: int):
        original_attention_init(self, config, layer_idx)
        if not _needs_gemma4_e2b_compat(config):
            return
        if self.has_kv:
            return

        self.has_kv = True
        dim = config.hidden_size
        self.k_proj = nn.Linear(dim, self.n_kv_heads * self.head_dim, bias=False)
        if not self.use_k_eq_v:
            self.v_proj = nn.Linear(dim, self.n_kv_heads * self.head_dim, bias=False)
        self.k_norm = nn.RMSNorm(self.head_dim, eps=config.rms_norm_eps)
        self.v_norm = module.RMSNormNoScale(self.head_dim, eps=config.rms_norm_eps)

    def patched_text_model_init(self, config):
        original_text_model_init(self, config)
        if _needs_gemma4_e2b_compat(config):
            self.previous_kvs = list(range(len(self.layers)))

    def patched_make_cache(self):
        if not _needs_gemma4_e2b_compat(self.args):
            return original_make_cache(self)

        caches = []
        for i in range(self.args.num_hidden_layers):
            if self.args.layer_types[i] == "full_attention":
                caches.append(module.KVCache())
            else:
                caches.append(
                    module.RotatingKVCache(
                        max_size=self.args.sliding_window,
                        keep=0,
                    )
                )
        return caches

    module.Attention.__init__ = patched_attention_init
    module.Gemma4TextModel.__init__ = patched_text_model_init
    module.Model.make_cache = patched_make_cache
    module._finetune_lab_gemma4_e2b_compat_applied = True


apply_patch()
