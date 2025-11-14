import 'package:flutter/material.dart';

class NovelScroll extends StatelessWidget {
  const NovelScroll({super.key, required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 600, // ← 任意の高さを指定
      child: SingleChildScrollView(
        padding: EdgeInsets.all(8),
        child: Text(text),
      ),
    );
  }
}
