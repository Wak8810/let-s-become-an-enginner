import 'package:flutter/material.dart';
import 'widgets/novel_scroll.dart';
import 'package:novel_app/models/novel.dart';

class NovelViewScreen extends StatefulWidget {
  const NovelViewScreen({
    super.key,
    required this.title,
    required this.text,
    required this.id,
  });
  final String title;
  final String text;
  final String id;

  @override
  State<NovelViewScreen> createState() => _NovelViewScreenState();
}

class _NovelViewScreenState extends State<NovelViewScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.id),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(widget.title),
            SizedBox(height: 10),
            NovelScroll(text: widget.text),
          ],
        ),
      ),
    );
  }
}
