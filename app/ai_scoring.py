# シンプルなスタブ：必要になったらOpenAIや自前モデルに差し替え
POSITIVE = ["最高","嬉しい","楽しい","好き","素晴らしい","すごい","good","great","awesome"]
NEGATIVE = ["最悪","悲しい","つらい","嫌い","無理","bad","terrible"]

def score_with_ai(text_: str) -> int:
    t = text_ or ""
    tl = t.lower()
    score = 0
    for w in POSITIVE:
        if w.lower() in tl:
            score += 10
    for w in NEGATIVE:
        if w.lower() in tl:
            score -= 8
    # 文章量ボーナス（最大+10）
    score += min(len(t) // 50, 10)
    # -100〜100の範囲にクリップ
    return max(-100, min(100, score))
