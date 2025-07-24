import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  List,
  Button,
  Input,
  Modal,
  Form,
  message,
  ConfigProvider,
  Image,
  Descriptions,
  Typography,
  Table,
  Popconfirm,
  Space,
  Spin
} from 'antd';
import 'antd/dist/reset.css';
import trTR from 'antd/locale/tr_TR';

const { Search } = Input;
const { Title } = Typography;

function App() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [selectedMovie, setSelectedMovie] = useState(null);

const handleLoadMovies = () => {
  axios.get('http://localhost:5001/')
    .then(res => {
      console.log("🎬 Gelen filmler:", res.data);
      setMovies(res.data);
    })
    .catch(err => console.error("Veri çekilemedi:", err));
};

const handleLoadFavorites = () => {
  axios.get("http://localhost:5001/favorites")
    .then(res => {
      setMovies(res.data);
      message.info("Favori filmler yüklendi.");
    })
    .catch(() => message.error("Favoriler alınamadı."));
};

  useEffect(() => {
    handleLoadMovies();
  }, []);

  const handleSearch = (value) => {
    if (!value) {
      message.warning("Lütfen bir başlık girin.");n
      return;
    }

    setLoading(true);
    axios.get(`http://localhost:5001/search?title=${value}`)
      .then(res => setMovies(res.data))
      .catch(() => {
        message.error("Eşleşen film bulunamadı.");
        setMovies([]);
      })
      .finally(() => setLoading(false));
  };

  const handleAddMovie = (values) => {
    axios.post('http://localhost:5001/movies', values)
      .then(() => {
        message.success("Film başarıyla eklendi.");
        setIsAddModalOpen(false);
        form.resetFields();
        handleLoadMovies();
      })
      .catch(() => {
        message.error("Film eklenemedi.");
      });
  };

  const handleAddFavorite = async (movie) => {
    try {
     await axios.post("http://localhost:5001/favorites", {
       title: movie.title,
        year: movie.year,
       score: movie.score,
       poster: movie.poster,
     });
      message.success("Favorilere eklendi!");
    } catch (err) {
     message.error("Favori eklenemedi.");
    }
  };



  const handleDelete = (year) => {
    axios.delete(`http://localhost:5001/movies/${year}`)
      .then(() => {
        message.success("Film silindi.");
        handleLoadMovies();
      })
      .catch(() => {
        message.error("Film silinemedi.");
      });
  };

  const handleExportCSV = () => {
    if (movies.length === 0) {
      message.warning("Export için veri yok.");
      return;
    }

    const headers = ["Title", "Year", "Score"];
    const rows = movies.map((movie) => [movie.title, movie.year, movie.score]);

    let csvContent = "data:text/csv;charset=utf-8,"
      + headers.join(",") + "\n"
      + rows.map(e => e.join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "filmler.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const columns = [
    {
      title: "Poster",
      dataIndex: "poster",
      key: "poster",
      render: (_, record) => (
        <Image
          src={
            record.poster && record.poster !== "N/A"
              ? record.poster
              : "https://dummyimage.com/60x90/cccccc/000000&text=No+Image"
          }
          alt="Poster"
          width={60}
        />
      ),
    },
    {
      title: "Başlık",
      dataIndex: "title",
      key: "title",
    },
    {
      title: "Yıl",
      dataIndex: "year",
      key: "year",
    },
    {
      title: "Puan",
      dataIndex: "score",
      key: "score",
    },
    {
      title: "İşlem",
      key: "actions",
      render: (_, record) => (
      <Space>
      <Button type="link" onClick={() => setSelectedMovie(record)}>Detay</Button>
      <Button type="default" onClick={() => handleAddFavorite(record)}>⭐ Favori</Button>
      <Popconfirm
        title="Bu filmi silmek istediğinize emin misiniz?"
        onConfirm={() => handleDelete(record.year)}
        okText="Evet"
        cancelText="İptal"
      >
        <Button danger>Sil</Button>
      </Popconfirm>
    </Space>
    ),
  },
  ];

  return (
    <ConfigProvider locale={trTR}>
      <div style={{ padding: 40 }}>
        <Title level={2} style={{ color: 'white', fontWeight: 'bold'}}>Film Uygulaması</Title>

        <div style={{ display: 'flex', gap: 20, marginBottom: 20 }}>
          <Button type="primary" onClick={handleLoadMovies}>Verileri Yükle</Button>
          <Search
            placeholder="Başlığa göre film ara"
            allowClear
            enterButton="Ara"
            onSearch={handleSearch}
            style={{ width: 300 }}
          />
          <Button type="dashed" onClick={() => setIsAddModalOpen(true)} style={{fontWeight: 'bold'}}> Film Ekle</Button>
          <Button onClick={handleExportCSV} style={{fontWeight: 'bold'}}> Export</Button>
        </div>

        {loading ? <Spin size="large" /> :
          <Table
            dataSource={movies.map(m => ({ ...m, key: m.title }))}
            columns={columns}
            pagination={{ pageSize: 6 }}
          />
        }

        {/* Yeni Film Ekle Modal */}
        <Modal
          title="Yeni Film Ekle"
          open={isAddModalOpen}
          onCancel={() => setIsAddModalOpen(false)}
          onOk={() => form.submit()}
          okText="Kaydet"
          cancelText="İptal"
        >
          <Form form={form} layout="vertical" onFinish={handleAddMovie}>
            <Form.Item name="title" label="Film Başlığı" rules={[{ required: true }]}> 
              <Input placeholder="Sadece başlık girin (örneğin: Inception)" />
            </Form.Item>
          </Form>
        </Modal>

        {/* Detay Modal */}
        <Modal
          title={selectedMovie?.title || "Film Detayı"}
          open={!!selectedMovie}
          onCancel={() => setSelectedMovie(null)}
          footer={null}
        >
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Yıl">{selectedMovie?.year}</Descriptions.Item>
            <Descriptions.Item label="Puan">{selectedMovie?.score}</Descriptions.Item>
            <Descriptions.Item label="Poster">
              <Image
                src={selectedMovie?.poster || "https://via.placeholder.com/120x160?text=No+Poster"}
                alt="Poster"
                width={120}
              />
            </Descriptions.Item>
          </Descriptions>
        </Modal>
      </div>
    </ConfigProvider>
  );
}

export default App;