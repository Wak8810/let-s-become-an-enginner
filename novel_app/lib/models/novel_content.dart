class NovelContent {
  final String text;
  final int lastChapter;
  final int totalChapters;

  NovelContent(
      {required this.text,
      required this.lastChapter,
      required this.totalChapters});

  factory NovelContent.fromJson(Map<String, dynamic> json) {
    return NovelContent(
      text: json['text'],
      lastChapter: json['last_chapter'],
      totalChapters: json['total_chapter_number'] as int? ?? 100,
    );
  }
}
