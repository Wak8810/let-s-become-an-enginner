import 'package:flutter/material.dart';
import 'package:novel_app/models/novel.dart';

class NovelCard extends StatelessWidget {
  final Novel novel;

  const NovelCard({super.key, required this.novel});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    novel.title,
                    style: const TextStyle(
                      fontSize: 18.0,
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                ),
                const SizedBox(width: 8.0),
                Text(
                  '要求時間: ${novel.readingMinutes}分',
                  textAlign: TextAlign.right,
                  style: const TextStyle(
                    fontSize: 12.0,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8.0),
            Text(
              novel.content,
              overflow: TextOverflow.ellipsis,
              maxLines: 1,
            ),
            const SizedBox(height: 8.0),
            Row(
              children: [
                const Spacer(),
                Text(
                  '作成日時: ${novel.createdAt}',
                  style: const TextStyle(
                    fontSize: 12.0,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
