class User {
  final String id;
  final String? userName;
  final String? email;
  final DateTime createdAt;
  final DateTime updatedAt;

  User({
    required this.id,
    this.userName,
    this.email,
    required this.createdAt,
    required this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['user_id'] as String,
      userName: json['user_name'] as String?,
      email: json['email'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}
