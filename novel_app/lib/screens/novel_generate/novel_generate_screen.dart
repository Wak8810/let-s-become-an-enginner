import 'package:flutter/material.dart';
import '../novel_view/novel_view_screen.dart';

class NovelGenerateScreen extends StatefulWidget {
  const NovelGenerateScreen({super.key});

  @override
  State<NovelGenerateScreen> createState() => _NovelGenerateScreenState();
}

class _NovelGenerateScreenState extends State<NovelGenerateScreen> {
  String isSelectedValue = 'あ';
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text("小説設定"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text("生成する小説の設定"),
            DropdownButton(
              items: const [
                DropdownMenuItem(value: 'あ', child: Text('あ')),
                DropdownMenuItem(value: 'い', child: Text('い')),
                DropdownMenuItem(value: 'う', child: Text('う')),
                DropdownMenuItem(value: 'え', child: Text('え')),
                DropdownMenuItem(value: 'お', child: Text('お')),
              ],
              value: isSelectedValue,
              onChanged: (String? value) {
                setState(() {
                  isSelectedValue = value!;
                });
              },
            ),
            ElevatedButton(
              child: Text("ViewPage"),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => NovelViewScreen(title: "ここに小説のタイトル"),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
