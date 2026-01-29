import { useEffect, useState } from 'react';
import { Container, Paper, Title, Text, Group, Badge, Loader, Button } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { userApi } from './api'; // Import instance kết nối cổng 5002

export function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // Lấy thông tin từ cổng 5002
        // Lưu ý: Nếu backend yêu cầu Token, bạn cần thêm Header Authorization
        const response = await userApi.get('/profile');
        setProfile(response.data.data);
      } catch (error) {
        console.error("Lỗi lấy thông tin profile:", error);
        alert("Phiên đăng nhập hết hạn!");
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  if (loading) return <Container ta="center" mt="xl"><Loader size="xl" /></Container>;

  return (
    <Container size="sm" my={40}>
      <Paper radius="md" withBorder p="xl" bg="var(--mantine-color-body)">
        <Group justify="space-between" mb="lg">
          <Title order={2}>Thông tin tài khoản</Title>
          <Badge size="lg" color="blue" variant="light">
            {/* Thêm dấu ? để tránh lỗi khi profile chưa load xong */}
            {profile?.role?.toUpperCase() || 'N/A'}
          </Badge>
        </Group>

        <div className="space-y-4">
          <Text size="sm"><strong>Họ tên:</strong> {profile?.name}</Text>
          <Text size="sm"><strong>Username:</strong> {profile?.username}</Text>
          <Text size="sm"><strong>Email:</strong> {profile?.email}</Text>
          <Text size="sm"><strong>Điện thoại:</strong> {profile?.telphone}</Text>
          <Text size="sm"><strong>Số Sensors:</strong> {profile?.sensors}</Text>
          <Text size="sm" c="dimmed">
            <strong>Ngày tạo:</strong> {new Date(profile?.created_at).toLocaleString()}
          </Text>
        </div>

        <Button fullWidth mt="xl" color="red" variant="outline" 
          onClick={() => { localStorage.clear(); navigate('/login'); }}>
          Đăng xuất
        </Button>
      </Paper>
    </Container>
  );
}