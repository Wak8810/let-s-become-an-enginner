class GeneratedNovel {
  final String title;
  final String firstChapterText;
  int totalChapterNumber;
  final String novelId;

  GeneratedNovel({
    required this.title,
    required this.novelId,
    required this.firstChapterText,
    required this.totalChapterNumber,
  });

  factory GeneratedNovel.fromJson(Map<String, dynamic> json) {
    return GeneratedNovel(
      title: json['title'] as String,
      firstChapterText: json['first_chapter_text'] as String,
      totalChapterNumber: json['total_chapter_number'] as int,
      novelId: json['novel_id'] as String,
    );
  }
}
