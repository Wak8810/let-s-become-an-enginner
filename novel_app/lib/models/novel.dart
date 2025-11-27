//入っている内容に追加する場合は編集可
//編集する場合は相談
class Novel {
  final String title;
  final String content;
  final DateTime createdAt;
  final int readingMinutes; // 読むのにかかる時間（分）
  final String novelId;
  final String overallPlot;
  final int textLength;

  Novel({
    required this.title,
    this.content = '', // content をデフォルト値付きの非nullable引数に変更
    required this.createdAt,
    this.readingMinutes = 0,
    required this.novelId,
    required this.overallPlot,
    required this.textLength,
  });

  factory Novel.fromJson(Map<String, dynamic> json) {
    return Novel(
      title: json['title'] as String,
      content: json['content'] as String? ?? '',
      readingMinutes: json['readingMinutes'] as int? ?? 0,
      createdAt: DateTime.parse(json['created_at'] as String),
      novelId: json['novel_id'] as String,
      overallPlot: json['overall_plot'] as String,
      textLength: json['text_length'] as int,
    );
  }
}
