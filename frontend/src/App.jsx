import React, { useState, useEffect } from 'react';
import { Container, Group, Button, Avatar, Text, Box } from '@mantine/core';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from './services/authService';
import { userService } from './services/userService';

function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => { checkLoginStatus(); }, []);

  const checkLoginStatus = async () => {
    try {
      const resp = await userService.getMyProfile();
      setUser(resp.data.data);
    } catch (err) {
      setUser(null);
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setUser(null);
      localStorage.clear();
      alert("Bạn đã đăng xuất thành công");
      navigate('/');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      <Box px="md" py="sm" sx={{ borderBottom: '1px solid #eee' }}>
        <Group position="apart">
          <Text weight={700}>My Microservices App</Text>
          <Group>
            <Button component={Link} to="/admin" variant="subtle">Admin</Button>

            {user ? (
              <Group>
                <Avatar radius="xl">{user.name ? user.name.charAt(0).toUpperCase() : 'U'}</Avatar>
                <Text>{user.name}</Text>
                <Button variant="outline" onClick={handleLogout}>Logout</Button>
              </Group>
            ) : null}
          </Group>
        </Group>
      </Box>

      <Container size="sm" mt="md">
        {user ? (
          <div>
            <Text size="xl" weight={700}>Xin chào, {user.name}</Text>
            <Text color="dimmed">Email: {user.email}</Text>
            <Text mt="md">Role: {user.role}</Text>
          </div>
        ) : null}
      </Container>
    </>
  );
}

export default App;