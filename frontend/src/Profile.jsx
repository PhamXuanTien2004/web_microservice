import { useEffect, useState } from 'react';
import { Container, Paper, Title, Text, Group, Badge, Loader, Button } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { userService } from './services/userService';

export function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // Lấy thông tin profile qua Gateway
        const response = await userService.getMyProfile();
        // Backend trả { status, data: { id, name, email, role, sensors, topic } }
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
          <Text size="sm"><strong>Email:</strong> {profile?.email}</Text>
          <Text size="sm"><strong>Role:</strong> {profile?.role}</Text>
          <Text size="sm"><strong>Số Sensors:</strong> {profile?.sensors ?? '—'}</Text>
          <Text size="sm"><strong>Topic:</strong> {profile?.topic ?? '—'}</Text>
        </div>

        <Button fullWidth mt="xl" color="red" variant="outline" 
          onClick={() => { localStorage.clear(); navigate('/login'); }}>
          Đăng xuất
        </Button>
      </Paper>
    </Container>
  );
}