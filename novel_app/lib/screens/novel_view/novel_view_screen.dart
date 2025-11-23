import 'package:flutter/material.dart';
import 'widgets/novel_scroll.dart';
import 'package:novel_app/models/novel.dart';

class NovelViewScreen extends StatefulWidget {
  const NovelViewScreen({super.key, required this.novel});
  final Novel novel;

  @override
  State<NovelViewScreen> createState() => _NovelViewScreenState();
}

class _NovelViewScreenState extends State<NovelViewScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.novel.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(widget.novel.title),
            SizedBox(height: 10),
            NovelScroll(text: widget.novel.content),
          ],
        ),
      ),
    );
  }
}
