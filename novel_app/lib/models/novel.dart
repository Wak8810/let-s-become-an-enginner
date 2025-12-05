//入っている内容に追加する場合は編集可
//編集する場合は相談
class Novel {
  final String title;
  final DateTime createdAt;
  final String novelId;
  final String shortSummary;
  final int textLength;
  final int trueTextLength;
  final int novelGeneratingStatus;

  Novel({
    required this.title,
    required this.createdAt,
    required this.novelId,
    required this.shortSummary,
    required this.textLength,
    this.trueTextLength = 0,
    required this.novelGeneratingStatus,
  });

  factory Novel.fromJson(Map<String, dynamic> json) {
    return Novel(
      novelId: json['novel_id'] as String,
      title: json['title'] as String,
      shortSummary: json['short_summary'] as String,
      textLength: json['text_length'] as int,
      trueTextLength: json['true_text_length'] as int,
      novelGeneratingStatus: json['novel_status'] as int,
      createdAt: DateTime.parse(json['created_at'] as String
      ),
    );
  }
}
