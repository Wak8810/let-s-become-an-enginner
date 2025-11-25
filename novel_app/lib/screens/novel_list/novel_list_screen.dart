import 'package:flutter/material.dart';
import 'package:novel_app/utils/get_user_all_novels.dart';
import 'package:novel_app/screens/novel_list/widgets/novel_card.dart';
import 'package:novel_app/models/novel.dart';
import 'package:novel_app/widgets/generate_novel_screen_button.dart';

class NovelListScreen extends StatefulWidget {
  const NovelListScreen({super.key});

  @override
  State<NovelListScreen> createState() => _NovelListScreenState();
}

class _NovelListScreenState extends State<NovelListScreen> {
  Future<List<Novel>>? _novels;

  @override
  void initState() {
    super.initState();
    _novels = GetUserAllNovels.fetchNovels();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('小説一覧')),
      body: FutureBuilder<List<Novel>>(
        future: _novels,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('小説がありません。'));
          } else {
            final novels = snapshot.data!;
            return ListView.builder(
              itemCount: novels.length,
              itemBuilder: (context, index) {
                return NovelCard(novel: novels[index]);
              },
            );
          }
        },
      ),
      floatingActionButton: const GenerateNovelScreen(),
    );
  }
}
