import 'package:flutter/material.dart';
import 'widgets/novel_scroll.dart';

class NovelViewScreen extends StatefulWidget {
  const NovelViewScreen({super.key, required this.title});
  final String title;

  @override
  State<NovelViewScreen> createState() => _NovelViewScreenState();
}

class _NovelViewScreenState extends State<NovelViewScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(widget.title),
            SizedBox(height: 10),
            NovelScroll(text: "ここに小説の文章が入る"),
          ],
        ),
      ),
    );
  }
}
