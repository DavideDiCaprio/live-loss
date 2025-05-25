package com.liveloss.app.service;

import com.liveloss.app.entity.User;
import com.liveloss.app.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.Optional;
import java.util.Arrays;
import java.util.List;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
public class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    public void testCreateUser() {
        // Given
        User user = new User("testuser", "test@example.com", "password");
        User savedUser = new User("testuser", "test@example.com", "password");
        savedUser.setId(1L);
        
        when(userRepository.save(user)).thenReturn(savedUser);
        
        // When
        User result = userService.createUser(user);
        
        // Then
        assertNotNull(result);
        assertEquals(1L, result.getId());
        assertEquals("testuser", result.getUsername());
        verify(userRepository, times(1)).save(user);
    }

    @Test
    public void testFindById() {
        // Given
        Long userId = 1L;
        User user = new User("testuser", "test@example.com", "password");
        user.setId(userId);
        
        when(userRepository.findById(userId)).thenReturn(Optional.of(user));
        
        // When
        Optional<User> result = userService.findById(userId);
        
        // Then
        assertTrue(result.isPresent());
        assertEquals(userId, result.get().getId());
        assertEquals("testuser", result.get().getUsername());
    }

    @Test
    public void testFindAll() {
        // Given
        User user1 = new User("user1", "user1@example.com", "password1");
        User user2 = new User("user2", "user2@example.com", "password2");
        List<User> users = Arrays.asList(user1, user2);
        
        when(userRepository.findAll()).thenReturn(users);
        
        // When
        List<User> result = userService.findAll();
        
        // Then
        assertNotNull(result);
        assertEquals(2, result.size());
        assertEquals("user1", result.get(0).getUsername());
        assertEquals("user2", result.get(1).getUsername());
    }

    @Test
    public void testDeleteUser() {
        // Given
        Long userId = 1L;
        
        // When
        userService.deleteUser(userId);
        
        // Then
        verify(userRepository, times(1)).deleteById(userId);
    }
}