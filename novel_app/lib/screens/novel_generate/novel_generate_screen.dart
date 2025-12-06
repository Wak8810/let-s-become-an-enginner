import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/services.dart';
import '../../models/genre.dart';
import '../../models/mood.dart';
import '../../utils/get_generate_settings.dart';
import '../../utils/get_mood_setting.dart';
import '../../screens/novel_generate/novel_generating_screen.dart';

class NovelGenerateScreen extends StatefulWidget {
  const NovelGenerateScreen({super.key});

  @override
  State<NovelGenerateScreen> createState() => _NovelGenerateScreenState();
}

class _NovelGenerateScreenState extends State<NovelGenerateScreen> {
  late Future<List<GenreData>> _genreFuture;
  late Future<List<MoodData>> _moodFuture;
  late String _userId;

  String selectedGenre = 'sf';
  int selectedTime = 0;
  int selectedUnit = 1;
  double selectedReadingSpeed = 1;
  String selectedStyle = '一人称視点';
  String selectedMood = 'none';
  bool canSubmit = false;

  @override
  void initState() {
    super.initState();
    _genreFuture = fetchGenreData();
    _moodFuture = fetchMoodData();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _userId = Provider.of<String>(context);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<dynamic>(
      future:Future.wait([_genreFuture, _moodFuture]),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        if (snapshot.hasError) {
          return Scaffold(body: Center(child: Text("エラー: ${snapshot.error}")));
        }

        if (!snapshot.hasData) return const SizedBox();

        final genres = snapshot.data!;
        if (selectedGenre.isEmpty) selectedGenre = genres[0].code;
        final moods = snapshot.data!;
        if (selectedGenre.isEmpty) selectedMood = moods[0].code;

        return Scaffold(
          backgroundColor: const Color(0xFFF5F5F7),
          appBar: AppBar(
            backgroundColor: Colors.white,
            elevation: 0,
            foregroundColor: Colors.black,
            title: const Text("小説設定"),
          ),
          body: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _sectionTitle("ジャンル"),
                _card(
                  child: DropdownButtonFormField<String>(
                    value: selectedGenre,
                    decoration: _inputDecoration(),
                    items: genres
                        .map(
                          (g) => DropdownMenuItem(
                            value: g.code,
                            child: Text(g.genre),
                          ),
                        )
                        .toList(),
                    onChanged: (v) => setState(() => selectedGenre = v!),
                  ),
                ),
                const SizedBox(height: 20),
                _sectionTitle("雰囲気"),
                _card(
                  child: DropdownButtonFormField<String>(
                    value: selectedGenre,
                    decoration: _inputDecoration(),
                    items: moods
                        .map(
                          (g) => DropdownMenuItem(
                            value: g.code,
                            child: Text(g.mood),
                          ),
                        )
                        .toList(),
                    onChanged: (v) => setState(() => selectedGenre = v!),
                  ),
                ),

                const SizedBox(height: 20),
                _sectionTitle("スタイル"),
                _card(
                  child: DropdownButtonFormField<String>(
                    value: selectedStyle,
                    decoration: _inputDecoration(),
                    items: const [
                      DropdownMenuItem(value: '一人称視点', child: Text('一人称視点')),
                      DropdownMenuItem(value: '三人称視点', child: Text('三人称視点')),
                    ],
                    onChanged: (v) => setState(() => selectedStyle = v!),
                  ),
                ),

                const SizedBox(height: 20),
                _sectionTitle("読書時間"),
                _card(
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          keyboardType: TextInputType.number,
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                          ],
                          decoration: _inputDecoration(label: "数値"),
                          onChanged: (value) {
                            setState(() {
                              selectedTime = int.tryParse(value) ?? 0;
                              canSubmit = selectedTime > 0;
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: DropdownButtonFormField<int>(
                          value: selectedUnit,
                          decoration: _inputDecoration(label: "単位"),
                          items: const [
                            DropdownMenuItem(value: 1, child: Text('分')),
                            DropdownMenuItem(value: 60, child: Text('時間')),
                          ],
                          onChanged: (v) => setState(() => selectedUnit = v!),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),
                _sectionTitle("読む速さ"),
                _card(
                  child: DropdownButtonFormField<double>(
                    value: selectedReadingSpeed,
                    decoration: _inputDecoration(),
                    items: const [
                      DropdownMenuItem(value: 1, child: Text('普通')),
                      DropdownMenuItem(value: 2, child: Text('速い')),
                      DropdownMenuItem(value: 0.7, child: Text('遅い')),
                    ],
                    onChanged: (v) => setState(() => selectedReadingSpeed = v!),
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
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                    onPressed: canSubmit
                        ? () {
                            Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(
                                builder: (context) => NovelGeneratingScreen(
                                  length:
                                      (selectedTime *
                                              selectedUnit *
                                              450 *
                                              selectedReadingSpeed.toInt())
                                          .toString(),
                                  genre: selectedGenre,
                                  style: selectedStyle,
                                  userId: _userId,
                                  mood:selectedMood
                                ),
                              ),
                            );
                          }
                        : null,
                    child: const Text("生成する", style: TextStyle(fontSize: 18)),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _sectionTitle(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 6),
    child: Text(
      text,
      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
    ),
  );

  Widget _card({required Widget child}) => Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(14),
      boxShadow: const [
        BoxShadow(color: Colors.black12, offset: Offset(0, 1), blurRadius: 4),
      ],
    ),
    child: child,
  );

  InputDecoration _inputDecoration({String? label}) => InputDecoration(
    labelText: label,
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
    filled: true,
    fillColor: const Color(0xFFF9F9FB),
    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
  );
}
