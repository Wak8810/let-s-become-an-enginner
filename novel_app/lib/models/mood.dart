class MoodData {
  final int id;
  final String code;
  final String mood;

  MoodData({required this.id, required this.code, required this.mood});

  factory MoodData.fromJson(Map<String, dynamic> json) {
    return MoodData(id: json['id'], code: json['code'], mood: json['mood']);
  }
}
