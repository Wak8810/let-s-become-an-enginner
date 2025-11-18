import 'package:flutter/material.dart';
import '../screens/novel_generate/novel_generate_screen.dart';

class GenerateNovelScreen extends StatelessWidget {
  const GenerateNovelScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.extended(
      onPressed: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => NovelGenerateScreen(),
          ),
        );
      },
      icon: const Icon(Icons.add),
      label: const Text('小説を生成する'),
    );
  }
}
