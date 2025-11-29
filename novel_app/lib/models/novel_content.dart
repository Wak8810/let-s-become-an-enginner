class NovelContent {
  final String novelId;
  final String title;
  final String text;

  NovelContent({required this.novelId, required this.title, required this.text});

  factory NovelContent.fromJson(Map<String, dynamic> json) {
    return NovelContent(
      novelId: json['novel_id'],
      title: json['title'],
      text: json['text'],
    );
  }
}
