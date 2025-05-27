import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';

class ApiService {
  final String baseUrl = 'http://192.168.202.14:8000'; // Ganti jika perlu
  String? _sessionId;

  // Inisialisasi session_id (local atau dari API)
  Future<void> initSession() async {
    if (_sessionId == null) {
      // Buat session_id lokal (alternatif: ambil dari backend jika kamu pakai endpoint /session)
      _sessionId = const Uuid().v4();
    }
  }

  Future<Map<String, dynamic>> predictTaskSuccess(Map<String, dynamic> inputData) async {
    final url = Uri.parse('$baseUrl/predict');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(inputData),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Gagal memuat prediksi');
    }
  }

  Future<String> askBot(String question) async {
    await initSession(); // Pastikan session_id tersedia

    final response = await http.post(
      Uri.parse('$baseUrl/ask'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'session_id': _sessionId,
        'message': question,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['response'] ?? 'Tidak ada jawaban dari bot.';
    } else {
      throw Exception('Gagal menghubungi server: ${response.statusCode}');
    }
  }
}
