class MoodData {
  final int id;
  final String code;
  final String genre;

  MoodData({required this.id, required this.code, required this.genre});

  factory MoodData.fromJson(Map<String, dynamic> json) {
    return MoodData(id: json['id'], code: json['code'], genre: json['genre']);
  }
}
