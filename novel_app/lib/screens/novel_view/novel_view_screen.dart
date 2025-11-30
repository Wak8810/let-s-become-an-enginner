import 'package:flutter/material.dart';
import 'widgets/novel_scroll.dart';

class NovelViewScreen extends StatelessWidget {
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
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text('閲覧ページ'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Expanded(child: NovelScroll(text: text)),
          ],
        ),
      ),
    );
  }
}
