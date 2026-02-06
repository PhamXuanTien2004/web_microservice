import { useEffect, useState } from 'react';
import { Container, Paper, Title, Text, Group, Badge, Loader, Button, Grid, Stack, Divider, Avatar, Box } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { userService } from './services/userService';
import { authService } from './services/authService';

export function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // Lấy thông tin profile qua Gateway
        const response = await userService.getMyProfile();
        console.log('Profile data:', response.data.data);
        setProfile(response.data.data);
      } catch (error) {
        console.error("Lỗi lấy thông tin profile:", error);
        alert("Phiên đăng nhập hết hạn!");
        navigate('/');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await authService.logout();
      localStorage.clear();
      alert("Bạn đã đăng xuất thành công");
      navigate('/');
    } catch (error) {
      console.error("Lỗi đăng xuất:", error);
      alert("Lỗi khi đăng xuất");
    }
  };

  if (loading) return <Container ta="center" mt="xl"><Loader size="xl" /></Container>;

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString('vi-VN');
    } catch {
      return dateString;
    }
  };

  return (
    <Container size="md" my={40}>
      <Paper radius="md" withBorder p="xl" bg="var(--mantine-color-body)">
        {/* Header với Avatar */}
        <Group mb="xl">
          <Avatar
            size={80}
            radius={80}
            src={null}
            color="blue"
            name={profile?.name}
          >
            {profile?.name?.charAt(0)?.toUpperCase() || 'U'}
          </Avatar>
          <div>
            <Title order={2}>{profile?.name || 'N/A'}</Title>
            <Text c="dimmed" size="sm">@{profile?.username || 'N/A'}</Text>
            <Badge size="lg" color="blue" variant="light" mt="xs">
              {profile?.role?.toUpperCase() || 'N/A'}
            </Badge>
          </div>
        </Group>

        <Divider my="lg" />

        {/* Thông tin cơ bản */}
        <Title order={4} mb="md">Thông tin cơ bản</Title>
        <Grid gutter="md" mb="lg">
          <Grid.Col span={{ base: 12, sm: 6 }}>
            <Box>
              <Text size="sm" fw={500} c="dimmed">Họ tên</Text>
              <Text size="sm">{profile?.name || 'N/A'}</Text>
            </Box>
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}>
            <Box>
              <Text size="sm" fw={500} c="dimmed">Username</Text>
              <Text size="sm">{profile?.username || 'N/A'}</Text>
            </Box>
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}>
            <Box>
              <Text size="sm" fw={500} c="dimmed">Email</Text>
              <Text size="sm">{profile?.email || 'N/A'}</Text>
            </Box>
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}>
            <Box>
              <Text size="sm" fw={500} c="dimmed">Số điện thoại</Text>
              <Text size="sm">{profile?.telphone || 'N/A'}</Text>
            </Box>
          </Grid.Col>
        </Grid>

        <Divider my="lg" />

        {/* Thông tin vai trò */}
        <Title order={4} mb="md">Thông tin vai trò</Title>
        <Grid gutter="md" mb="lg">
          <Grid.Col span={{ base: 12, sm: 6 }}>
            <Box>
              <Text size="sm" fw={500} c="dimmed">Vai trò</Text>
              <Badge size="md" color={profile?.role === 'admin' ? 'red' : 'blue'}>
                {profile?.role?.toUpperCase() || 'N/A'}
              </Badge>
            </Box>
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}>
            <Box>
              <Text size="sm" fw={500} c="dimmed">ID</Text>
              <Text size="sm">{profile?.id || 'N/A'}</Text>
            </Box>
          </Grid.Col>
        </Grid>

        {/* Thông tin cảm biến (chỉ hiển thị nếu là user) */}
        {profile?.role === 'user' && (
          <>
            <Divider my="lg" />
            <Title order={4} mb="md">Thông tin cảm biến</Title>
            <Grid gutter="md" mb="lg">
              <Grid.Col span={{ base: 12, sm: 6 }}>
                <Box>
                  <Text size="sm" fw={500} c="dimmed">Số cảm biến</Text>
                  <Text size="sm">{profile?.sensors ?? 'N/A'}</Text>
                </Box>
              </Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6 }}>
                <Box>
                  <Text size="sm" fw={500} c="dimmed">Topic MQTT</Text>
                  <Text size="sm" style={{ wordBreak: 'break-all' }}>{profile?.topic || 'N/A'}</Text>
                </Box>
              </Grid.Col>
            </Grid>
          </>
        )}

        <Divider my="lg" />

        {/* Thông tin hệ thống */}
        <Title order={4} mb="md">Thông tin hệ thống</Title>
        <Box mb="lg">
          <Text size="sm" fw={500} c="dimmed">Ngày tạo tài khoản</Text>
          <Text size="sm">{formatDate(profile?.created_at)}</Text>
        </Box>

        <Button fullWidth mt="xl" color="red" variant="outline" 
          onClick={handleLogout}>
          Đăng xuất
        </Button>
      </Paper>
    </Container>
  );
}