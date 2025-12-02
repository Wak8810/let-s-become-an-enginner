import 'package:flutter/material.dart';
import '../../utils/generate_novel.dart';
import '../novel_view/novel_view_screen.dart';
import '../../models/generated_novel.dart';

class NovelGeneratingScreen extends StatefulWidget {
  const NovelGeneratingScreen({
    super.key,
    required this.genre,
    required this.length,
    required this.style,
  });
  final String genre;
  final String length;
  final String style;

  @override
  State<NovelGeneratingScreen> createState() => _NovelGeneratingScreenState();
}

class _NovelGeneratingScreenState extends State<NovelGeneratingScreen> {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<GeneratedNovel>(
      future: fetchGeneratedNovel(
        widget.length,
        widget.genre,
        widget.style,
      ), // ← APIここで呼ぶ
      builder: (context, snapshot) {
        // 通信中
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Scaffold(
            backgroundColor: Colors.white,
            body: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 20),
                  const Text(
                    "小説を生成しています…",
                    style: TextStyle(fontSize: 16, color: Colors.black87),
                  ),
                ],
              ),
            ),
          );
        }

        // エラー
        if (snapshot.hasError) {
          return Scaffold(
            backgroundColor: Colors.white,
            body: Center(
              child: Container(
                padding: const EdgeInsets.all(20),
                margin: const EdgeInsets.symmetric(horizontal: 40),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 10,
                      offset: Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.error_outline,
                      size: 40,
                      color: Colors.red,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      "エラーが発生しました。\n${snapshot.error}",
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 14),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: () => setState(() {}),
                      child: const Text("もう一度試す"),
                    ),

                    ElevatedButton(
                      onPressed: () {
                        Navigator.pop(context);
                      },
                      child: const Text("小説一覧に戻る"),
                    ),
                  ],
                ),
              ),
            ),
          );
        }

        // データ取得完了
        if (snapshot.hasData) {
          // 画面遷移は WidgetsBinding で次フレームに回すと安全
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(
                builder: (context) => NovelViewScreen(
                  title: snapshot.data!.title,
                  text: snapshot.data!.firstChapterText,
                  novelId: snapshot.data!.novelId,
                  finalChapterIndex: 1,
                  totalChapterNumber: snapshot.data!.totalChapterNumber,
                ),
              ),
            );
          });

          // 遷移するまでの間に空の Container を返す
          return Container();
        }
        return Container();
      },
    );
  }
}
