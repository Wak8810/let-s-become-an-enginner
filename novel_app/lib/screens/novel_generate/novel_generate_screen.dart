import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../models/genre.dart';
import '../../utils/get_generate_settings.dart';
import '../../screens/novel_generate/novel_generating_screen.dart';

class NovelGenerateScreen extends StatefulWidget {
  const NovelGenerateScreen({super.key});

  @override
  State<NovelGenerateScreen> createState() => _NovelGenerateScreenState();
}

class _NovelGenerateScreenState extends State<NovelGenerateScreen> {
  late Future<List<GenreData>> _genreFuture; // ← Future を保持
  String selectedGenre = '';
  int selectedTime = 0;
  int selectedUnit = 1;
  String selectedStyle = '三人称';

  @override
  void initState() {
    super.initState();
    _genreFuture = fetchGenreData(); // ← initState で1回だけ呼ぶ
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<GenreData>>(
      future: _genreFuture, // ← build のたびに再実行されない
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text("エラー: ${snapshot.error}"));
        }

        if (snapshot.hasData) {
          final genres = snapshot.data!;
          if (selectedGenre.isEmpty) {
            selectedGenre = genres[0].code; // 初回のみ代入
          }

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
                  // ===== ジャンル =====
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
                      child: DropdownMenu<String>(
                        initialSelection: selectedGenre,
                        label: const Text("ジャンル"),
                        dropdownMenuEntries: genres
                            .map(
                              (g) => DropdownMenuEntry<String>(
                                value: g.code,
                                label: g.genre,
                              ),
                            )
                            .toList(),
                        onSelected: (value) {
                          if (value != null) {
                            setState(() {
                              selectedGenre = value;
                            });
                          }
                        },
                      ),
                    ),
                  ),

                  // ===== 読書時間・単位・ボタン =====
                  const Text(
                    "スタイル",
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
                      child: DropdownMenu<String>(
                        initialSelection: selectedGenre,
                        label: const Text("スタイル"),
                        dropdownMenuEntries: [
                          DropdownMenuEntry(value: '一人称視点', label: '一人称視点'),
                          DropdownMenuEntry(value: '三人称視点', label: '三人称視点'),
                        ],
                        onSelected: (value) {
                          if (value != null) {
                            setState(() {
                              selectedStyle = value;
                            });
                          }
                        },
                      ),
                    ),
                  ),
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
                                  selectedTime = int.parse(value);
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
                          Expanded(
                            child: DropdownButtonFormField(
                              items: const [
                                DropdownMenuItem(value: 1, child: Text('分')),
                                DropdownMenuItem(value: 60, child: Text('時間')),
                              ],
                              initialValue: selectedUnit,
                              onChanged: (int? value) {
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

                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.black,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onPressed: () {
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(
                            builder: (context) => NovelGeneratingScreen(
                              length: (selectedTime * selectedUnit * 450)
                                  .toString(),
                              genre: selectedGenre,
                              style: selectedStyle,
                            ),
                          ),
                        );
                      },
                      child: const Text("生成する", style: TextStyle(fontSize: 18)),
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
