export type View = "beginner-guide" | "onboarding" | "overview" | "data" | "runs" | "compare";

export const ALL_VIEWS: View[] = ["beginner-guide", "onboarding", "overview", "data", "runs", "compare"];

export type Audience = "新手" | "工程" | "进阶";

export const AUDIENCE_KEY: Record<Audience, "novice" | "eng" | "advanced"> = {
  "新手": "novice",
  "工程": "eng",
  "进阶": "advanced",
};
