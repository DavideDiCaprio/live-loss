package com.liveloss.app.integration;

import com.liveloss.app.entity.User;
import com.liveloss.app.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.TestPropertySource;
import com.fasterxml.jackson.databind.ObjectMapper;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(locations = "classpath:application-test.properties")
public class UserControllerIntegrationTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ObjectMapper objectMapper;

    private String baseUrl;

    @BeforeEach
    public void setUp() {
        baseUrl = "http://localhost:" + port + "/api/users";
        userRepository.deleteAll();
    }

    @Test
    public void testCreateUser() {
        // Given
        User user = new User("testuser", "test@example.com", "password");
        
        // When
        ResponseEntity<User> response = restTemplate.postForEntity(baseUrl, user, User.class);
        
        // Then
        assertEquals(HttpStatus.CREATED, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("testuser", response.getBody().getUsername());
        assertEquals("test@example.com", response.getBody().getEmail());
        assertNotNull(response.getBody().getId());
    }

    @Test
    public void testGetUserById() {
        // Given
        User user = new User("testuser", "test@example.com", "password");
        User savedUser = userRepository.save(user);
        
        // When
        ResponseEntity<User> response = restTemplate.getForEntity(
            baseUrl + "/" + savedUser.getId(), User.class);
        
        // Then
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("testuser", response.getBody().getUsername());
        assertEquals(savedUser.getId(), response.getBody().getId());
    }

    @Test
    public void testGetAllUsers() {
        // Given
        User user1 = new User("user1", "user1@example.com", "password1");
        User user2 = new User("user2", "user2@example.com", "password2");
        userRepository.save(user1);
        userRepository.save(user2);
        
        // When
        ResponseEntity<User[]> response = restTemplate.getForEntity(baseUrl, User[].class);
        
        // Then
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(2, response.getBody().length);
    }

    @Test
    public void testGetUserByIdNotFound() {
        // When
        ResponseEntity<User> response = restTemplate.getForEntity(baseUrl + "/999", User.class);
        
        // Then
        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
    }

    @Test
    public void testDeleteUser() {
        // Given
        User user = new User("testuser", "test@example.com", "password");
        User savedUser = userRepository.save(user);
        
        // When
        restTemplate.delete(baseUrl + "/" + savedUser.getId());
        
        // Then
        ResponseEntity<User> response = restTemplate.getForEntity(
            baseUrl + "/" + savedUser.getId(), User.class);
        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
    }
}