import 'package:flutter/material.dart';

class ViewNovelPage extends StatefulWidget {
  const ViewNovelPage({super.key, required this.title});
  final String title;

  @override
  State<ViewNovelPage> createState() => _ViewNovelPageState();
}

class _ViewNovelPageState extends State<ViewNovelPage> {
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
            Text(widget.title),SizedBox(height: 10),SizedBox(
    height: 600, // ← 任意の高さを指定
    child: SingleChildScrollView(
      padding: EdgeInsets.all(8),
      child: Text(
        "ここに小説の文章が入る"
      ),
    ),
  )]),
)
    );
  }
}
