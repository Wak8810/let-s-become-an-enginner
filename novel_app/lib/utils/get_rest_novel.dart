import 'package:http/http.dart' as http;
import 'dart:convert';

String userId = 'e116fe527f714ba4a34f512f29196ac2';

Future<(String,int)> fetchRestNovel(
  int finalChapterIndex, //現在の最終チャプター番号
  String novelId,
) async {
  final url = Uri.parse('http://localhost:5000/novels/$novelId/contents');
  
  final response = await http.get(
    url,
    headers: {'Content-Type': 'application/json','X-User-ID':userId,'X-Current-Index':(finalChapterIndex).toString()}
  );

  if (response.statusCode == 200) {
    final response_json = json.decode(response.body);
    List contents=  response_json['new_chapters'];
    String text='';
    int lastIndex = contents.length+ finalChapterIndex;    for(var content  in contents){
      text+=content['content'];
    }
    return (text,lastIndex);
  } else {
    final error = jsonDecode(response.body);
    throw Exception(error["message"]);
  }
}
