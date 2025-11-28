import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../models/genre.dart';

Future<List<GenreData>> fetchGenreData() async {
  final url = Uri.parse('http://10.0.2.2:5000/genres/');
  final response = await http.get(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    final List<dynamic> decodedJson = jsonDecode(response.body);
    final List<GenreData> genreList = decodedJson
        .map((e) => GenreData.fromJson(e))
        .toList();
    return genreList;
  } else {
    final error = jsonDecode(response.body);
    throw Exception(error["message"]);
  }
}
