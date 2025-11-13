import 'package:flutter/material.dart';

class NovelListScreen extends StatelessWidget {
  const NovelListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('小説一覧'), // 画面上部にタイトルを表示
      ),
      body: Container(
        color: Colors.white, // これで本文領域が白くなります
        child: const Center(
          child: Text('ここに小説リストが表示'), // 仮のテキスト
        ),
      ),
    );
  }
}