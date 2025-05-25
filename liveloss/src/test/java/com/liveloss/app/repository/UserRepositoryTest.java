package com.liveloss.app.repository;

import com.liveloss.app.entity.User;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
public class UserRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private UserRepository userRepository;

    @Test
    public void testFindByUsername() {
        // Given
        User user = new User("testuser", "test@example.com", "password");
        entityManager.persistAndFlush(user);
        
        // When
        Optional<User> found = userRepository.findByUsername("testuser");
        
        // Then
        assertTrue(found.isPresent());
        assertEquals("testuser", found.get().getUsername());
        assertEquals("test@example.com", found.get().getEmail());
    }

    @Test
    public void testFindByEmail() {
        // Given
        User user = new User("testuser", "test@example.com", "password");
        entityManager.persistAndFlush(user);
        
        // When
        Optional<User> found = userRepository.findByEmail("test@example.com");
        
        // Then
        assertTrue(found.isPresent());
        assertEquals("testuser", found.get().getUsername());
        assertEquals("test@example.com", found.get().getEmail());
    }

    @Test
    public void testExistsByUsername() {
        // Given
        User user = new User("testuser", "test@example.com", "password");
        entityManager.persistAndFlush(user);
        
        // When
        boolean exists = userRepository.existsByUsername("testuser");
        
        // Then
        assertTrue(exists);
    }

    @Test
    public void testExistsByEmail() {
        // Given
        User user = new User("testuser", "test@example.com", "password");
        entityManager.persistAndFlush(user);
        
        // When
        boolean exists = userRepository.existsByEmail("test@example.com");
        
        // Then
        assertTrue(exists);
    }

    @Test
    public void testFindByUsernameNotFound() {
        // When
        Optional<User> found = userRepository.findByUsername("nonexistent");
        
        // Then
        assertFalse(found.isPresent());
    }
}