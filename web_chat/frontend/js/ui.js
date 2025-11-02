/* UI components for rendering messages and UI elements */

/**
 * Render a message bubble
 */
function renderMessage(message, container) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message--${message.role}`;
    messageDiv.setAttribute('data-message-id', message.id || generateId());
    
    const bubble = document.createElement('div');
    bubble.className = 'message__bubble';
    
    const content = document.createElement('div');
    content.className = 'message__content';
    
    // Render markdown/content
    if (message.content) {
        content.innerHTML = renderMarkdown(message.content);
    }
    
    // Check for image paths in content and render them
    const imagePaths = extractImagePaths(message.content);
    if (imagePaths.length > 0) {
        imagePaths.forEach(imagePath => {
            const imgContainer = createImageElement(imagePath);
            content.appendChild(imgContainer);
        });
    }
    
    // Check for video paths in content and render them
    const videoPaths = extractVideoPaths(message.content);
    if (videoPaths.length > 0) {
        videoPaths.forEach(videoPath => {
            const videoContainer = createVideoElement(videoPath);
            content.appendChild(videoContainer);
        });
    }
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message__timestamp';
    if (message.timestamp) {
        timestamp.textContent = formatTimestamp(message.timestamp);
    }
    
    bubble.appendChild(content);
    bubble.appendChild(timestamp);
    messageDiv.appendChild(bubble);
    
    // Render function calls if any
    if (message.function_calls && message.function_calls.length > 0) {
        message.function_calls.forEach(funcCall => {
            const funcCallElement = renderFunctionCall(funcCall);
            messageDiv.appendChild(funcCallElement);
            
            // Check if function call result contains image path
            if (funcCall.result && funcCall.result.stdout) {
                const imagePath = extractImagePathFromOutput(funcCall.result.stdout);
                if (imagePath) {
                    const imgContainer = createImageElement(imagePath);
                    funcCallElement.appendChild(imgContainer);
                }
                
                // Check for video path
                const videoPath = extractVideoPathFromOutput(funcCall.result.stdout);
                if (videoPath) {
                    const videoContainer = createVideoElement(videoPath);
                    funcCallElement.appendChild(videoContainer);
                }
            }
        });
    }
    
    container.appendChild(messageDiv);
    scrollToBottom(container);
    
    return messageDiv;
}

/**
 * Render markdown content (basic implementation)
 */
function renderMarkdown(text) {
    if (!text) return '';
    
    // Escape HTML first
    let html = escapeHtml(text);
    
    // Convert markdown links [text](url) to HTML links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="message__link" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Convert code blocks ```language\ncode\n```
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<div class="message__code-block"><code>${escapeHtml(code.trim())}</code></div>`;
    });
    
    // Convert inline code `code`
    html = html.replace(/`([^`]+)`/g, '<code style="background-color: var(--color-gray-ultra-light); padding: 2px 4px; border-radius: 3px;">$1</code>');
    
    // Convert bold **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Convert italic *text*
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Convert line breaks
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

/**
 * Render function call indicator with collapsible details
 */
function renderFunctionCall(functionCall) {
    const funcCallDiv = document.createElement('div');
    funcCallDiv.className = 'message message--function-call';
    
    const funcCallBubble = document.createElement('div');
    funcCallBubble.className = 'message__function-call';
    
    const header = document.createElement('div');
    header.className = 'message__function-call__header';
    header.style.cursor = 'pointer';
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';
    
    const nameAndStatus = document.createElement('div');
    nameAndStatus.style.flex = '1';
    
    const name = document.createElement('div');
    name.className = 'message__function-call__name';
    name.textContent = `Calling: ${functionCall.name}`;
    
    const status = document.createElement('div');
    status.className = 'message__function-call__status';
    
    if (functionCall.status === 'pending' || functionCall.status === 'executing') {
        const spinner = document.createElement('span');
        spinner.className = 'message__function-call__spinner';
        status.appendChild(spinner);
        status.appendChild(document.createTextNode(` ${functionCall.status}...`));
    } else if (functionCall.status === 'completed') {
        status.textContent = '✓ Completed';
    } else if (functionCall.status === 'failed') {
        status.textContent = '✗ Failed';
    }
    
    nameAndStatus.appendChild(name);
    nameAndStatus.appendChild(status);
    
    const toggleIcon = document.createElement('span');
    toggleIcon.textContent = '▼';
    toggleIcon.className = 'message__function-call__toggle';
    toggleIcon.style.marginLeft = '8px';
    toggleIcon.style.fontSize = '12px';
    toggleIcon.style.transition = 'transform 0.2s';
    
    header.appendChild(nameAndStatus);
    header.appendChild(toggleIcon);
    
    const details = document.createElement('div');
    details.className = 'message__function-call__details';
    details.style.display = 'none';
    details.style.marginTop = '8px';
    details.style.paddingTop = '8px';
    details.style.borderTop = '1px solid rgba(255, 255, 255, 0.2)';
    details.style.fontSize = '12px';
    
    // Show arguments if available
    if (functionCall.args && Object.keys(functionCall.args).length > 0) {
        const argsLabel = document.createElement('div');
        argsLabel.style.fontWeight = '600';
        argsLabel.style.marginBottom = '4px';
        argsLabel.textContent = 'Arguments:';
        details.appendChild(argsLabel);
        
        const argsDiv = document.createElement('pre');
        argsDiv.style.margin = '0';
        argsDiv.style.fontSize = '11px';
        argsDiv.style.opacity = '0.9';
        argsDiv.textContent = JSON.stringify(functionCall.args, null, 2);
        details.appendChild(argsDiv);
    }
    
    // Show result if available
    if (functionCall.result) {
        const resultLabel = document.createElement('div');
        resultLabel.style.fontWeight = '600';
        resultLabel.style.marginTop = '8px';
        resultLabel.style.marginBottom = '4px';
        resultLabel.textContent = 'Result:';
        details.appendChild(resultLabel);
        
        const resultDiv = document.createElement('pre');
        resultDiv.style.margin = '0';
        resultDiv.style.fontSize = '11px';
        resultDiv.style.opacity = '0.9';
        resultDiv.style.maxHeight = '200px';
        resultDiv.style.overflow = 'auto';
        
        // Format result
        if (typeof functionCall.result === 'object') {
            resultDiv.textContent = JSON.stringify(functionCall.result, null, 2);
        } else {
            resultDiv.textContent = String(functionCall.result);
        }
        details.appendChild(resultDiv);
    }
    
    // Toggle functionality
    let isExpanded = false;
    header.addEventListener('click', () => {
        isExpanded = !isExpanded;
        if (isExpanded) {
            details.style.display = 'block';
            toggleIcon.textContent = '▲';
            toggleIcon.style.transform = 'rotate(180deg)';
        } else {
            details.style.display = 'none';
            toggleIcon.textContent = '▼';
            toggleIcon.style.transform = 'rotate(0deg)';
        }
    });
    
    funcCallBubble.appendChild(header);
    funcCallBubble.appendChild(details);
    funcCallDiv.appendChild(funcCallBubble);
    
    return funcCallDiv;
}

/**
 * Show error message
 */
function showError(message, container) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    container.appendChild(errorDiv);
    scrollToBottom(container);
    
    // Remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

/**
 * Show loading indicator
 */
function showLoading(container) {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message message--assistant';
    loadingDiv.id = 'loading-indicator';
    
    const bubble = document.createElement('div');
    bubble.className = 'message__bubble';
    bubble.innerHTML = '<span class="loading"></span> Thinking...';
    
    loadingDiv.appendChild(bubble);
    container.appendChild(loadingDiv);
    scrollToBottom(container);
    
    return loadingDiv;
}

/**
 * Extract video paths from text content
 */
function extractVideoPaths(text) {
    if (!text) return [];
    
    const videoPaths = [];
    // Look for common video path patterns
    const patterns = [
        /(?:File path:|Saved to:|Video saved to:|Generated video saved to:)\s*([^\s\n]+\.(?:mp4|webm|mov|avi))/gi,
        /public\/videos\/[^\s\n]+\.(?:mp4|webm|mov|avi)/gi,
        /(?:file|path|output|video):\s*([^\s\n]+\.(?:mp4|webm|mov|avi))/gi
    ];
    
    patterns.forEach(pattern => {
        const matches = text.match(pattern);
        if (matches) {
            matches.forEach(match => {
                // Extract just the path part
                const pathMatch = match.match(/([^\s\n]+\.(?:mp4|webm|mov|avi))/i);
                if (pathMatch && pathMatch[1]) {
                    const path = pathMatch[1].trim();
                    if (!videoPaths.includes(path)) {
                        videoPaths.push(path);
                    }
                }
            });
        }
    });
    
    return videoPaths;
}

/**
 * Extract video path from function call output
 */
function extractVideoPathFromOutput(stdout) {
    if (!stdout) return null;
    
    // Look for file path in stdout
    const patterns = [
        /(?:File path:|Saved to:|Video saved to:|Generated video saved to:)\s*([^\s\n]+\.(?:mp4|webm|mov|avi))/i,
        /public\/videos\/[^\s\n]+\.(?:mp4|webm|mov|avi)/i,
        /([^\s\n]+\.(?:mp4|webm|mov|avi))/i
    ];
    
    for (const pattern of patterns) {
        const match = stdout.match(pattern);
        if (match && match[1]) {
            return match[1].trim();
        }
    }
    
    return null;
}

/**
 * Create a video element for display
 */
function createVideoElement(videoPath) {
    const videoContainer = document.createElement('div');
    videoContainer.className = 'message__video-container';
    videoContainer.style.marginTop = '12px';
    videoContainer.style.marginBottom = '12px';
    
    const video = document.createElement('video');
    video.className = 'message__video';
    video.style.maxWidth = '100%';
    video.style.height = 'auto';
    video.style.borderRadius = '8px';
    video.style.border = '1px solid var(--color-border)';
    video.controls = true;
    video.preload = 'metadata';
    
    // Try to load video from various possible paths
    const possiblePaths = [
        videoPath,
        `/${videoPath}`,
        `http://localhost:5001/${videoPath}`,
        videoPath.startsWith('public/') ? videoPath.replace('public/', '/') : videoPath,
        videoPath.startsWith('public/') ? videoPath.replace('public/', '/') : `/${videoPath}`
    ];
    
    // Use a better video loading strategy
    let currentPathIndex = 0;
    const tryLoadVideo = () => {
        if (currentPathIndex < possiblePaths.length) {
            video.src = possiblePaths[currentPathIndex];
            currentPathIndex++;
        } else {
            // All paths failed, show placeholder
            video.style.border = '2px dashed var(--color-border)';
            const placeholder = document.createElement('div');
            placeholder.style.padding = '20px';
            placeholder.style.textAlign = 'center';
            placeholder.style.color = 'var(--color-gray-medium)';
            placeholder.textContent = `Video not found: ${videoPath}`;
            videoContainer.replaceChild(placeholder, video);
        }
    };
    
    video.onloadedmetadata = () => {
        // Video loaded successfully
    };
    
    video.onerror = () => {
        tryLoadVideo();
    };
    
    tryLoadVideo();
    
    videoContainer.appendChild(video);
    
    // Add video path as caption
    const caption = document.createElement('div');
    caption.className = 'message__video-caption';
    caption.style.fontSize = '11px';
    caption.style.color = 'var(--color-gray-medium)';
    caption.style.marginTop = '4px';
    caption.style.fontFamily = 'var(--font-family-mono)';
    caption.textContent = videoPath;
    videoContainer.appendChild(caption);
    
    return videoContainer;
}

/**
 * Extract image paths from text content
 */
function extractImagePaths(text) {
    if (!text) return [];
    
    const imagePaths = [];
    // Look for common image path patterns
    const patterns = [
        /(?:File path:|Saved to:|Image saved to:|Generated image saved to:)\s*([^\s\n]+\.(?:png|jpg|jpeg|gif|webp))/gi,
        /public\/images\/[^\s\n]+\.(?:png|jpg|jpeg|gif|webp)/gi,
        /(?:file|path|output|image):\s*([^\s\n]+\.(?:png|jpg|jpeg|gif|webp))/gi
    ];
    
    patterns.forEach(pattern => {
        const matches = text.match(pattern);
        if (matches) {
            matches.forEach(match => {
                // Extract just the path part
                const pathMatch = match.match(/([^\s\n]+\.(?:png|jpg|jpeg|gif|webp))/i);
                if (pathMatch && pathMatch[1]) {
                    const path = pathMatch[1].trim();
                    if (!imagePaths.includes(path)) {
                        imagePaths.push(path);
                    }
                }
            });
        }
    });
    
    return imagePaths;
}

/**
 * Extract image path from function call output
 */
function extractImagePathFromOutput(stdout) {
    if (!stdout) return null;
    
    // Look for file path in stdout
    const patterns = [
        /(?:File path:|Saved to:|Image saved to:|Generated image saved to:)\s*([^\s\n]+\.(?:png|jpg|jpeg|gif|webp))/i,
        /public\/images\/[^\s\n]+\.(?:png|jpg|jpeg|gif|webp)/i,
        /([^\s\n]+\.(?:png|jpg|jpeg|gif|webp))/i
    ];
    
    for (const pattern of patterns) {
        const match = stdout.match(pattern);
        if (match && match[1]) {
            return match[1].trim();
        }
    }
    
    return null;
}

/**
 * Create an image element for display
 */
function createImageElement(imagePath) {
    const imgContainer = document.createElement('div');
    imgContainer.className = 'message__image-container';
    imgContainer.style.marginTop = '12px';
    imgContainer.style.marginBottom = '12px';
    
    const img = document.createElement('img');
    img.className = 'message__image';
    img.style.maxWidth = '100%';
    img.style.height = 'auto';
    img.style.borderRadius = '8px';
    img.style.border = '1px solid var(--color-border)';
    img.style.cursor = 'pointer';
    
    // Try to load image from various possible paths
    const possiblePaths = [
        imagePath,
        `/${imagePath}`,
        `http://localhost:5001/${imagePath}`,
        imagePath.startsWith('public/') ? imagePath.replace('public/', '/') : imagePath,
        imagePath.startsWith('public/') ? imagePath.replace('public/', '/') : `/${imagePath}`
    ];
    
    // Use a better image loading strategy
    let currentPathIndex = 0;
    const tryLoadImage = () => {
        if (currentPathIndex < possiblePaths.length) {
            img.src = possiblePaths[currentPathIndex];
            currentPathIndex++;
        } else {
            // All paths failed, show placeholder
            img.alt = 'Image not found';
            img.style.border = '2px dashed var(--color-border)';
            const placeholder = document.createElement('div');
            placeholder.style.padding = '20px';
            placeholder.style.textAlign = 'center';
            placeholder.style.color = 'var(--color-gray-medium)';
            placeholder.textContent = `Image not found: ${imagePath}`;
            imgContainer.replaceChild(placeholder, img);
        }
    };
    
    img.onload = () => {
        imageLoaded = true;
    };
    
    img.onerror = () => {
        tryLoadImage();
    };
    
    tryLoadImage();
    
    img.addEventListener('click', () => {
        // Open image in new tab
        window.open(img.src, '_blank');
    });
    
    imgContainer.appendChild(img);
    
    // Add image path as caption
    const caption = document.createElement('div');
    caption.className = 'message__image-caption';
    caption.style.fontSize = '11px';
    caption.style.color = 'var(--color-gray-medium)';
    caption.style.marginTop = '4px';
    caption.style.fontFamily = 'var(--font-family-mono)';
    caption.textContent = imagePath;
    imgContainer.appendChild(caption);
    
    return imgContainer;
}

