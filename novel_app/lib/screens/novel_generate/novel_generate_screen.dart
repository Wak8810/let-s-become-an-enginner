import 'package:flutter/material.dart';
import '../novel_view/novel_view_screen.dart';
import 'dart:convert';
import 'package:novel_app/models/novel.dart';
import 'package:flutter/services.dart';

class NovelGenerateScreen extends StatefulWidget {
  const NovelGenerateScreen({super.key});

  @override
  State<NovelGenerateScreen> createState() => _NovelGenerateScreenState();
}

class _NovelGenerateScreenState extends State<NovelGenerateScreen> {
  String isSelectedGenre = 'ファンタジー';
  String isSelectedTime = '0';
  String isSelectedUnit = '分';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color.fromARGB(255, 255, 255, 255),
        title: const Text("小説設定"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ======== ジャンル ========
            const Text(
              "ジャンル",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: DropdownButtonFormField(
                  decoration: const InputDecoration(border: InputBorder.none),
                  items: const [
                    DropdownMenuItem(value: 'ファンタジー', child: Text('ファンタジー')),
                    DropdownMenuItem(value: 'ホラー', child: Text('ホラー')),
                    DropdownMenuItem(value: 'サスペンス', child: Text('サスペンス')),
                    DropdownMenuItem(value: 'ギャグ', child: Text('ギャグ')),
                  ],
                  value: isSelectedGenre,
                  onChanged: (String? value) {
                    setState(() {
                      isSelectedGenre = value!;
                    });
                  },
                ),
              ),
            ),

            const SizedBox(height: 24),

            // ======== 読書時間 ========
            const Text(
              "読書時間",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),

            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    // 数値欄
                    Expanded(
                      child: TextField(
                        keyboardType: TextInputType.number,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly,
                        ],
                        onChanged: (value) {
                          setState(() {
                            isSelectedTime = value;
                          });
                        },
                        decoration: InputDecoration(
                          labelText: "数値",
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          isDense: true,
                        ),
                      ),
                    ),

                    const SizedBox(width: 16),

                    // 単位
                    Expanded(
                      child: DropdownButtonFormField(
                        items: const [
                          DropdownMenuItem(value: '分', child: Text('分')),
                          DropdownMenuItem(value: '時間', child: Text('時間')),
                        ],
                        value: isSelectedUnit,
                        onChanged: (String? value) {
                          setState(() {
                            isSelectedUnit = value!;
                          });
                        },
                        decoration: InputDecoration(
                          labelText: "単位",
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          isDense: true,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const Spacer(),

            // ======== 決定ボタン ========
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: () {
                  List<dynamic> decodedJson = json.decode(dummyNovelsJson);
                  Novel novel = Novel.fromJson(
                    decodedJson[0] as Map<String, dynamic>,
                  );

                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (context) => NovelViewScreen(novel: novel),
                    ),
                  );
                },
                child: const Text("ViewPage", style: TextStyle(fontSize: 18)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

String dummyNovelsJson = """
      [
        {
          "title": "普通の小説",
          "content": "普通の内容",
          "created_at": "2025-11-15T10:00:00Z",
          "reading_minutes": 5
        }
      ]""";
