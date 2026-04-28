package ai.finetunelab.edgebench.litertlm;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import com.google.ai.edge.litertlm.Backend;
import com.google.ai.edge.litertlm.Conversation;
import com.google.ai.edge.litertlm.ConversationConfig;
import com.google.ai.edge.litertlm.Engine;
import com.google.ai.edge.litertlm.EngineConfig;
import com.google.ai.edge.litertlm.LogSeverity;
import com.google.ai.edge.litertlm.Message;
import java.util.Collections;

public final class MainActivity extends Activity {
  private static final String TAG = "LiteRTLMEdgeSmoke";

  private TextView output;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    output = new TextView(this);
    output.setTextSize(16f);
    output.setPadding(32, 48, 32, 32);
    output.setText("LiteRT-LM smoke starting...");
    setContentView(output);

    String modelPath = getIntent().getStringExtra("model_path");
    if (modelPath == null || modelPath.isEmpty()) {
      modelPath = "/data/local/tmp/edge-bench/gemma-4-E2B-it.litertlm";
    }
    String prompt = getIntent().getStringExtra("prompt");
    if (prompt == null || prompt.isEmpty()) {
      prompt = "What is the capital of France?";
    }

    final String finalModelPath = modelPath;
    final String finalPrompt = prompt;
    new Thread(() -> runSmoke(finalModelPath, finalPrompt), "litert-lm-smoke").start();
  }

  private void runSmoke(String modelPath, String prompt) {
    long start = System.currentTimeMillis();
    try {
      Log.i(TAG, "SMOKE_START model=" + modelPath + " prompt=" + prompt);
      Engine.Companion.setNativeMinLogSeverity(LogSeverity.ERROR);
      EngineConfig engineConfig =
          new EngineConfig(
              modelPath,
              new Backend.CPU(null),
              null,
              null,
              null,
              null,
              getCacheDir().getPath());
      try (Engine engine = new Engine(engineConfig)) {
        engine.initialize();
        ConversationConfig conversationConfig =
            new ConversationConfig(
                null,
                Collections.emptyList(),
                Collections.emptyList(),
                null,
                true,
                null,
                Collections.emptyMap());
        try (Conversation conversation = engine.createConversation(conversationConfig)) {
          Message message = conversation.sendMessage(prompt, Collections.emptyMap());
          long elapsed = System.currentTimeMillis() - start;
          String text = message.toString();
          Log.i(TAG, "SMOKE_OK elapsed_ms=" + elapsed + " text=" + text);
          show("OK (" + elapsed + "ms)\n\n" + text);
        }
      }
    } catch (Throwable throwable) {
      Log.e(TAG, "SMOKE_ERROR", throwable);
      show("ERROR\n\n" + Log.getStackTraceString(throwable));
    }
  }

  private void show(String text) {
    runOnUiThread(() -> output.setText(text));
  }
}
