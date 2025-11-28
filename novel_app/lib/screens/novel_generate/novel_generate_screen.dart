import 'package:flutter/material.dart';
import '../novel_view/novel_view_screen.dart';
import 'dart:convert';
import 'package:novel_app/models/novel.dart';
import 'package:flutter/services.dart';
import '../../models/genre.dart';
import 'get_generate_settings.dart';

class NovelGenerateScreen extends StatefulWidget {
  const NovelGenerateScreen({super.key});

  @override
  State<NovelGenerateScreen> createState() => _NovelGenerateScreenState();
}

class _NovelGenerateScreenState extends State<NovelGenerateScreen> {
  String selectedGenre = '';
  String selectedTime = '0';
  String selectedUnit = '分';

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<GenreData>>(
      future: fetchGenreData(), // ← APIここで呼ぶ
      builder: (context, snapshot) {
        // 通信中
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        // エラー
        if (snapshot.hasError) {
          return Center(child: Text("エラー: ${snapshot.error}"));
        }

        // データ取得完了
        if (snapshot.hasData) {
          final genres = snapshot.data!;
          selectedGenre = genres[0].code;

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

                      child: DropdownButtonFormField<String>(
                        initialValue: selectedGenre,
                        decoration: const InputDecoration(
                          border: InputBorder.none,
                        ),
                        items: genres.map((g) {
                          return DropdownMenuItem(
                            value: g.code, // ← value も genre だけ
                            child: Text(g.genre),
                          );
                        }).toList(),
                        onChanged: (value) {
                          if (value != null) {
                            setState(() {
                              selectedGenre = value; // 型安全に代入
                            });
                          }
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
                                  selectedTime = value;
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
                                DropdownMenuItem(
                                  value: '時間',
                                  child: Text('時間'),
                                ),
                              ],
                              value: selectedUnit,
                              onChanged: (String? value) {
                                setState(() {
                                  selectedUnit = value!;
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
                        List<dynamic> decodedJson = json.decode(
                          dummyNovelsJson,
                        );
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
                      child: const Text(
                        "ViewPage",
                        style: TextStyle(fontSize: 18),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        }

        return const SizedBox();
      },
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
