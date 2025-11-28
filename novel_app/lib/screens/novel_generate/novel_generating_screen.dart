import 'package:flutter/material.dart';
import '../../utils/generate_novel.dart';
import '../novel_view/novel_view_screen.dart';
import 'package:novel_app/models/novel.dart';
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
          return const Center(child: CircularProgressIndicator());
        }

        // エラー
        if (snapshot.hasError) {
          return Center(child: Text("エラー: ${snapshot.error}"));
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
                  id: snapshot.data!.novelId,
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
