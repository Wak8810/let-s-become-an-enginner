class GenreData {
  final int id;
  final String code;
  final String genre;

  GenreData({required this.id, required this.code, required this.genre});

  factory GenreData.fromJson(Map<String, dynamic> json) {
    return GenreData(id: json['id'], code: json['code'], genre: json['genre']);
  }
}
