import 'package:flutter/material.dart';

class NovelScroll extends StatelessWidget {
  const NovelScroll({super.key, required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 16,
          height: 1.6, // 行間を少し広げる
        ),
      ),
    );
  }
}
