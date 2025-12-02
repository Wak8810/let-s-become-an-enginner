import 'package:flutter/material.dart';
import 'package:novel_app/models/novel.dart';
//import 'package:novel_app/models/novel_content.dart';
import 'package:novel_app/utils/get_novel_content.dart';

class NovelCard extends StatelessWidget {
  final Novel novel;
  final String userId;

  const NovelCard({super.key, required this.novel, required this.userId});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () async {
        try {
          final novelContent =
              await GetNovelContent.fetchNovelContent(novel.novelId, userId);
        } catch (e) {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('小説の読み込みに失敗しました: $e'),
              ),
            );
          }
        }
      },
      child: Card(
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
                        fontSize: 14.0,
                        fontWeight: FontWeight.bold,
                      ),
                      overflow: TextOverflow.ellipsis,
                      maxLines: 1,
                    ),
                  ),
                  const SizedBox(width: 8.0),
                  Text(
                    '文字数: ${novel.textLength}文字',
                    textAlign: TextAlign.right,
                    style: const TextStyle(
                      fontSize: 12.0,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12.0),
              Text(
                novel.overallPlot,
                overflow: TextOverflow.ellipsis,
                maxLines: 1,
              ),
              const SizedBox(height: 12.0),
              Row(
                children: [
                  const Spacer(),
                  Text(
                    '作成日時: ${novel.createdAt}',
                    style: const TextStyle(
                      fontSize: 10.0,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

