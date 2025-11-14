//入っている内容に追加する場合は編集可
//編集する場合は相談
class Novel {
  final String title;
  final String content;
  final DateTime createdAt;

  Novel({
    required this.title,
    required this.content,
    required this.createdAt,
  });

  factory Novel.fromJson(Map<String, dynamic> json) {
    return Novel(
      title: json['title'] as String,
      content: json['content'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
