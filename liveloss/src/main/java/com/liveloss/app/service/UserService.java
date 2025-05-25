package com.liveloss.app.service;

import com.liveloss.app.entity.User;
import com.liveloss.app.repository.UserRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class UserService {
    
    private final UserRepository userRepository;
    
    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public User createUser(User user) {
        return userRepository.save(user);
    }
    
    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }
    
    public List<User> findAll() {
        return userRepository.findAll();
    }
    
    public User updateUser(Long id, User userDetails) {
        return userRepository.findById(id)
            .map(user -> {
                user.setUsername(userDetails.getUsername());
                user.setEmail(userDetails.getEmail());
                user.setPassword(userDetails.getPassword());
                return userRepository.save(user);
            })
            .orElseThrow(() -> new RuntimeException("User not found with id: " + id));
    }
    
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}