# 第2回 解答

## 演習

- 使ったモデル・設定：`Qwen/Qwen3.5-0.8B`（revision `2fc06364715b967f1860aea9cf38778875588b17`）、seed 42、LoRA `r=16`、学習率 `2e-4`、20 エポック。Google Colab の T4 GPU、量子化なし、評価は greedy 生成。結果の詳細は [`results/baseline/result.json`](results/baseline/result.json)。
- 学習の実行：講師の結果は使わず、この Colab T4 で新規に学習を実行した。ノートブックの `executed_training_myself` は `true`。操作・集計には Codex を使用した。
- 学習前：`format_rate` = 2/21（9.5%） / `content_rate` = 0/21（0%）。多くの出力で `needs_review` キーが欠けた。
- 学習後：`format_rate` = 21/21（100%） / `content_rate` = 19/21（90.5%）。
- 退行した質問：なし（形式と内容の両方に合格した質問を基準に比較）。
- 学習後に残った失敗：`成績はいつ出ますか` と `オフィスアワーは事前予約が必要ですか` は、FAQ に根拠がないのに `needs_review: false` で別項目の情報を当てはめて断定した。原文は [`results/baseline/eval_after.json`](results/baseline/eval_after.json)。
- 知識を問う質問（セクション 6）：FAQ にない「最終課題の締切」は `format_error → asserted`（FAQ にある別の締切を流用）。「担当教員の名前」「次回の講義テーマ」はともに `format_error → needs_review`。FAQ にある「課題の提出期限」は `format_error → asserted` で、学習後の回答内容は FAQ と一致した。
- 学習で変わったこと・変わらなかったこと：JSON 形式は全問で守られるようになった。一方、根拠のない質問への断定は残り、形式遵守と根拠判断は別に評価する必要がある。

## 宿題

- 取り組んだレベル：**基礎**。
- 変えた設定：`CONFIG["num_train_epochs"]` だけを **20 → 10** に変更。T4 のセッションを再起動して上から実行した。モデル、revision、seed、データ分割、LoRA 設定、学習率、生成条件、評価用の 21 問は同じ。学習前の 21 件の出力原文も両条件で一致した。

| 指標 | 元設定：20 エポック | 変更後：10 エポック |
|---|---:|---:|
| ステップ数 | 40 | 20 |
| 学習前 `format_rate` | 2/21（9.5%） | 2/21（9.5%） |
| 学習前 `content_rate` | 0/21（0%） | 0/21（0%） |
| 学習後 `format_rate` | 21/21（100%） | 21/21（100%） |
| 学習後 `content_rate` | 19/21（90.5%） | 18/21（85.7%） |
| 最終ログ loss | 0.0142（step 40） | 0.0990（step 20） |
| 学習時間 | 223.8 秒 | 110.6 秒 |

- 最終 loss は `trainer.state.log_history` の最後の `loss`、学習時間は `train_runtime` を使用した。各条件の `result.json` と `training_metrics.json` は [元設定](results/baseline/result.json) と [変更後](results/epochs10/result.json) のフォルダに保存した。質問別の出力も両フォルダの `eval_before.json`、`eval_after.json` で確認できる。
- 10 エポックでは、FAQ にある「PDF 以外でも出せますか」に確認要求で逃げた。FAQ にない「文字数制限」「参考文献の書き方」は `needs_review: true` だったが、回答に採点基準の語句「確認」がなく内容不合格となった。20 エポック側の不合格 2 問は、いずれも根拠なしへの断定だった。学習回数を半分にすると、この実行では時間と loss に加えて内容正解率も変わった。ただし各条件 1 回ずつであり、GPU 上の学習には揺れがあるため、1 問の差を一般的な効果とは断定しない。
- ファインチューニングが向く場面：固定された JSON 形式や文体を繰り返し出力させたいとき。向かない場面：FAQ にない事実の判断や、頻繁に更新される情報への回答。今回も形式は両条件で 100% になったが、根拠のない回答や確認文の欠落が残った。事実の正確さには、元資料の検索と根拠の照合を組み合わせる必要がある。
