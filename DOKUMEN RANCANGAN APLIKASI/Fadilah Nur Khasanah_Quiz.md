Bagian 1. Identitas dan Topik Proyek Aplikasi
    a. Nama aplikasi : FrameFit
    b. Deskripsi singkat dan tujuan utama aplikasi : FrameFit merupakan aplikasi berbabis AI dan Computer Vision yg membantu user menentukan bentuk wajah dan memilih frame kacamata yg sesuai. User cukup mengupload foto wajah, kemudian sistem akan menganalisis bentuk wajah menggunakan model mobilenetv2. Setelah dianalisis hasilnya akan digunakan untuk menentukan frame yg cocok, kemudian user dapat melihat visualisasi wajah mereka menggunakan frame yg direkomendasikan sistem dengan fitur virtual try-on. Tujuan utama aplikasi ini adalah memudahkan memilih frame kacamata yg biasanya dilakukan dengan mencoba berbagai frame secara langsung. Dengan Framefit, user dapat gambaran mengenai bentuk wajah, rekomendasi frame kacamata, dan visual (user) saat menggunakan frame tersebut secara digital sebelum membeli frame secara langsung.
    c. Target pengguna utama :
        1. Masyarakat umum yg ingin mengetahui bentuk   wajah dan model frame kacamata yg sesuai
        2. Remaja/mahasiswa yg ingin memilih kacamata secara praktis
        3. User e-commerce yg ingin memperoleh gamabran kacamata sebelum membeli
        4. Toko optik yg ingin menyediakan layanan pemilihan kacamata berbasis digital

Bagian 2. Resume Modul Digital Awareness
    1. Modul 1 There's a whole new world out there
        Teknologi digital membantu manusia menyelesaikan berbagai perkerjaan dengan lebih cepat dan praktis. Perubahan dari proses analog ke digital membuat aktivitas seperti mencari informasi, berkomunikasi, menyimpan data, dan menggunakan layanan dapat dilakukan melalui perangkat digital. Namun, pengunaan terknologi tetap membutuhkan pemahaman agar teknologi digunakan secara tepat dan memberikan manfaat bagi user.

    2. Modul 2 You`ll need some basic tools
        Penggunaan teknologi membutuhkan pemahaman dasar mengenai perangkat keras, sistem operasi, file dan folder, serta keamanan akun. User perlu mengetahui cara mengelola file dengan baik dan menggunakan kata sandi yg kuat untuk mengurangi risiko akses yg tidak sah. Pemahaman tersebut menjadi bagian penting agar user dapat mengunakan aplikasi secara aman dan mandiri.

    3. Modul 3 This is how you get around and find what you`re looking for
        Internet menyediakan banyak informasi sehingga user perlu mengetahui cara menggunakan browser dan melakukan pencarian informasi secara efektif. Informasi dari internet juga harus diperiksa sumber dan penggunaannya, terutama ketika menggunakan gambar, library, dataset, atau digital lainnya. User dan developer perlu memahami perbedaan antara copyright, opensource, dan public domain agar tidak menggunakan aset secara sembarangan.

    4. Modul 4 It just keeps getting better
        Perkembangan teknologi, khususnya AI, memberikan banyak peluang untuk membantu pekerjaan manusia. Namun, penggunaan AI harus tetap memperhatikan etika, tanggung jawab, dan dampaknya terhadap user. Selain itu, komunikasi di internet harus dilakukan dengan memperhatikan netiquette, sehingga teknologi tidak digunakan untuk melakukan tindakan yg merugikan orang lain.

    5. Modul 5 Even though it`s digital, it is real, with real consequences
        Data digital tetap memiliki konsekuensi nyata sehingga pribadi harus dijaga dengan baik. User perlu memahami risiko penyebaran Personally Identifiable Information, jejak digital, penipuan, pembajakan, dan komunikasi negatif di internet. data yg sudah dibagikan secara digital juga dapat sulit dihapus sepenuhnya sehingga pengguna perlu berhari hati sebelum memberikan informasi.

    6. Modul 6 Learn about anything and everything
        Kemampuan digital tidak hanya berkaitan dengan pengguna aplikasi, tetapi juga kemampuan memecahkan masalah ketika terjadi kendala teknis. User perlu mengetahuilangkah dasar troubleshooting, seperti memeriksa koneksi, konfigurasi perangkat, dan pesan kesalahan. Selain itu, seseorang perlu mengetahui kemampuan digital yg sudah dimiliki dan kemampuan yg masih perlu dikembangkan.

Bagian 3. Hubungan dan Implementasi pada Topik Proyek
    1. Bagaimana rancangan aplikasi dapat mempermudah tugas sehari-hari pengguna? Apa proses “analog/tradisional” dari topik proyekmu yang berhasil disederhanakan menjadi digital.
    Jawaban : FrameFit mempermudah proses pemilihan frame kacamata yg sebelumnya dilakukan secara manual. secara tradisional, user perlu mencoba beberapa frame secara langsung atau meminta bantuan orang lain untuk menentukan model yg sesuai dengan bentuk wajah user. Pada FrameFit, proses tersebut disederhanakan menjadi proses digital. User hanya mengupload foto wajah, kemudian sistem menganalisis bentuk wajah menggunakan mobilenetv2. Hasil analisis digunakan untuk memberikan rekomendasi frame, kemudian user dapat melihat simulasi penggunakan frame melalui virtual try-on. Dengan demikian, proses yg sebelumnya membutuhkan percobaan secara langsung dapat dilakukan terlebih dahulu melalui aplikasi sehingga user dapat memperoleh gamabran awal dengan lebih praktis.

    2. Jika aplikasimu memiliki fitur penyimpanan file atau pendaftaran akun, bagaimana kamu merancang struktur penyimpanan file yang intuitif bagi pengguna awam? Bagaimana kamu membantu pengguna membuat kata sandi yang aman?
    Jawaban : FrameFit tidak membutuhkan user untuk menyimpan banyak file secara manual karena input utama sistem berupa foto wajah dalam format jpg atau png. User cukup menggugah foto melalui antarmuka aplikasi dan sistem menangani proses pemrosesan gambar di backend. kebutuhan sistem memang menetapkan dukungan terhadap foto jpg dan png. JIka sistem nanti menyediakan penyimpanan hasil analisis, file dapat dikelompokkan berdasarkan janisnya, misalnya:
        1. Foto user
        2. Hasil analisis
        3. Hasil virtual try-on
    Struktur tersebut dibuat sederhana agar pengguna awam tidak perlu memahami struktur folder atau proses teknis di dalam sistem. Untuk keamanan akun, apabila fitur ditambahkan, aplikasi dapat memberikan aturan seperti:
        1. Menggunakan kata sandi minimal dengan panjang tertentu,
        2. mengombinasikan huruf besar, huruf kecil, angka, dan karakter khusus,
        3. Tidak menggunakan informasi pribadi sebagai kata sandi,
        4. Tidak menggunakan kata sandi yg sama untuk banyak akun.

    3. Bagaimana kamu mendesain fitur pencarian (searchbar) di dalam aplikasi agar pengguna dapat mencari informasi dengan mudah? Selain itu, sebutkan asset eksternal yang digunakan dalam aplikasi (library, API, gambar, icon). Apakah asset-aset tersebut berlisensi open-source, public domain, atau memiliki hak cipta khusus yang wajib dicantumkan?
    Jawaban : FrameIt tidak menyediakan kolom pencarian teks (search bar). Hal ini disesuaikan dengan tujuan utama aplikasi, yaitu membantu pengguna awam menemukan rekomendasi kacamata berdasarkan hasil analisis bentuk wajah, bukan menjelajahi katalog dalam jumlah besar. Setelah pengguna mengunggah foto, sistem menganalisis bentuk wajah menggunakan MobileNetV2 dan secara otomatis menentukan beberapa frame yang sesuai melalui Recommendation Engine. Dengan pendekatan tersebut, pengguna tidak perlu menentukan kata kunci atau mencari model satu per satu. Katalog frame digunakan sebagai sumber pilihan yang kemudian disesuaikan dengan hasil analisis bentuk wajah. Sistem juga menampilkan informasi frame seperti gambar, nama/model, kategori atau bentuk frame, sehingga pengguna dapat memahami pilihan yang diberikan. Untuk asset eksternal, pengembangan FrameIt menggunakan dataset dan teknologi pendukung seperti Face Shape Dataset, Glasses Segmentation Synthetic Dataset, MobileNetV2, MediaPipe Face Landmarker, dan OpenCV. Penggunaan dataset maupun asset eksternal perlu memperhatikan lisensi dan ketentuan penggunaannya. Proposal mencatat bahwa Face Shape Dataset digunakan untuk klasifikasi bentuk wajah, sedangkan Glasses Segmentation Synthetic Dataset digunakan sebagai pendukung proses Computer Vision.

    4. Jika aplikasimu memiliki fitur interaksi social,bagaimana kamu mencegah pelanggaran etika digital di  dalamnya? Jika aplikasi menggunakan fitur pintar berbasis AI, bagaimana kamu memastikan AI tersebut bekerja secara etis dan bertanggung jawab bagi pengguna?
    Jawaban : FrameFit tidak memiliki fitur sosial sebagai fungsi utama, sehingga risiko pelanggaran etika dalam komunikasi antar user relatif terbatas. Namun, aplikasi tetap perlu menjaga keamanan dan privasi foto wajah user karena foto wajah termasuk data yg dapat berkaitan dengan identitas seseorang. Dalam penggunaan AI, hasil klasifikasi juga perlu disampaikan sebagai hasil prediksi, bukan sebagai kebenaran mutlak. Sistem menampilkan bentuk wajah beserta confidence score sehingga pengguna dapat memahami bahwa hasil tersebut berasal dari prediksi model. Fitur klasifikasi FrameIt memang dirancang untuk menghasilkan label bentuk wajah dan confidence. AI berperan dalam menganalisis bentuk wajah pengguna dan menentukan rekomendasi kacamata berdasarkan hasil analisis tersebut. Informasi yang dihasilkan kemudian digunakan untuk membantu pengguna menemukan model kacamata yang sesuai dengan karakteristik wajahnya.

    5. Data pribadi sensitive (PII) apa saja yang dikumpulkan oleh aplikasimu? Bagaimana cara kamu melindungi data tersebut agar tidak bocor atau disalahgunakan? Bagaimana aplikasi meminimalkan Risiko pengguna menjadi korban penipuan siber di platform mu?
    Jawaban : 
    Data utama yang digunakan FrameIt adalah foto wajah pengguna. Foto tersebut diperlukan untuk melakukan analisis bentuk wajah dan proses Virtual Try-On. Karena foto wajah berkaitan dengan identitas seseorang, pengguna perlu diberi informasi mengenai tujuan penggunaan foto tersebut. Beberapa langkah yang dapat diterapkan untuk mengurangi risiko penyalahgunaan data adalah:
        1. Hanya mengumpulkan data yang diperlukan untuk menjalankan fitur;
        2. Tidak meminta informasi pribadi yang tidak berhubungan dengan fungsi aplikasi;
        3. Menggunakan koneksi HTTPS ketika mengirim data antara frontend dan backend;
        4. Membatasi akses terhadap data pengguna;
        5. Tidak membagikan foto pengguna tanpa persetujuan;
        6. Menghapus foto apabila sudah tidak diperlukan, jika sistem tidak membutuhkan penyimpanan permanen.
    Risiko penipuan juga dapat dikurangi dengan tidak meminta informasi sensitif yang tidak diperlukan, seperti nomor kartu pembayaran atau password akun lain. Selain itu, antarmuka dapat memberikan informasi yang jelas mengenai data apa yang digunakan dan untuk tujuan apa sehingga pengguna tidak memberikan data secara tidak sadar.

    6. Ketika aplikasi mengalami masalah teknis (misalnya kehilangan koneksi internet atau kegagalan memuat data), bagaimana aplikasi mengomunikasikannya kepada pengguna? Tuliskan contoh rancangan pesan error ramah pengguna yang memandu pengguna melakukan troubleshooting mandiri secara mudah.
    Jawaban : FrameIt harus memberikan pesan kesalahan yang mudah dipahami dan tidak hanya menampilkan pesan teknis seperti “Internal Server Error”. Pesan harus menjelaskan masalah dan memberikan langkah sederhana yang dapat dilakukan pengguna. Contohnya: 
        1. Jika foto gagal diunggah, alertnya kira kira "Foto gagal diunggah. Pastikan ukuran dan format foto sesuai. Gunakan foto JPG atau PNG, lalu coba unggah kembali."
        2. Jika wajah tidak terdeteksi, alernya kira kira "Wajah belum terdeteksi. Pastikan wajah terlihat jelas, tidak tertutup, dan berada di tengah foto. Coba gunakan foto dengan pencahayaan yang lebih baik."
        3. Jika koneksi internet bermasalah, alertnya kira kira "Koneksi tidak tersedia. Periksa koneksi internet Anda, kemudian coba kembali beberapa saat lagi."
        4. Jika proses analisis gagal, alertnya kira kira "Analisis belum dapat dilakukan. Terjadi kendala saat memproses foto. Silakan coba dengan foto lain atau ulangi proses beberapa saat lagi."
    Hal ini penting karena salah satu keterbatasan sistem adalah hasil analisis dapat dipengaruhi oleh kualitas foto, pencahayaan, posisi wajah, dan sudut pengambilan gambar.