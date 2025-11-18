import 'package:flutter/material.dart';

class GenerateNovelScreen extends StatelessWidget {
  const GenerateNovelScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.extended(
      onPressed: () {
        print('clicked!');
      },
      icon: const Icon(Icons.add),
      label: const Text('小説を生成する'),
    );
  }
}
