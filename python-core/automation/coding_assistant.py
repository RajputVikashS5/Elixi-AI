"""
Coding Assistant Module - Stage 5 Phase 2
Provides intelligent code generation, debugging, explanation, and refactoring
"""

import ast
import re
import time
from typing import Any, Dict, Optional, List
from datetime import datetime
from stage5_base import BaseAnalyzer
from stage5_utils import Logger, TextProcessor


class CodingAssistant(BaseAnalyzer):
    """Intelligent coding assistant with AI-powered code analysis and generation"""
    
    def __init__(self, mongodb=None, ai_brain=None, enable_cache: bool = True):
        """Initialize coding assistant.
        
        Args:
            mongodb: MongoDB connection for caching
            ai_brain: AI brain instance for generation
            enable_cache: Whether to enable caching
        """
        super().__init__("CodingAssistant", mongodb, enable_cache)
        self.ai_brain = ai_brain
        self.supported_languages = [
            'python', 'javascript', 'java', 'csharp', 'cpp', 
            'sql', 'html', 'css', 'typescript', 'go', 'rust'
        ]
        Logger.info(self.name, "Ready with multi-language support")
    
    def analyze(self, code: str, language: str = None) -> Dict[str, Any]:
        """Analyze code structure and quality.
        
        Args:
            code: Code to analyze
            language: Programming language (auto-detect if None)
            
        Returns:
            Analysis results with metrics and suggestions
        """
        start_time = time.time()
        
        if not code or not code.strip():
            return self.format_error("Code cannot be empty", "EMPTY_CODE")
        
        # Auto-detect language if not provided
        if not language:
            language = TextProcessor.detect_language(code)
        
        # Check cache
        cache_key = self.get_cache_key(action='analyze', code=code, language=language)
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, "Returning cached analysis")
            return cached
        
        # Perform analysis based on language
        analysis = {
            'language': language,
            'lines': len(code.split('\n')),
            'characters': len(code),
            'syntax_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'complexity': 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        # Python-specific analysis
        if language == 'python':
            python_analysis = self._analyze_python(code)
            analysis.update(python_analysis)
        
        # JavaScript/TypeScript analysis
        elif language in ['javascript', 'typescript']:
            js_analysis = self._analyze_javascript(code)
            analysis.update(js_analysis)
        
        # Generic code metrics
        else:
            generic_analysis = self._analyze_generic(code)
            analysis.update(generic_analysis)
        
        # Add AI interpretation if available
        if self.ai_brain:
            try:
                ai_analysis = self._get_ai_analysis(code, language)
                if ai_analysis:
                    analysis['ai_insights'] = ai_analysis
            except Exception as e:
                Logger.warning(self.name, f"AI analysis failed: {e}")
        
        duration_ms = (time.time() - start_time) * 1000
        self.log_analysis(f"{language} code", f"{len(analysis['errors'])} errors", duration_ms)
        
        # Cache result
        result = self.format_success(analysis, "Code analysis complete")
        self.cache_result(cache_key, result, ttl_minutes=30)
        
        return result
    
    def generate_code(self, description: str, language: str, context: str = None) -> Dict[str, Any]:
        """Generate code from natural language description.
        
        Args:
            description: What the code should do
            language: Programming language to generate
            context: Optional context or existing code
            
        Returns:
            Generated code with explanation
        """
        start_time = time.time()
        
        if not description or not description.strip():
            return self.format_error("Description cannot be empty", "EMPTY_DESCRIPTION")
        
        if language not in self.supported_languages:
            return self.format_error(
                f"Language '{language}' not supported. Supported: {', '.join(self.supported_languages)}",
                "UNSUPPORTED_LANGUAGE"
            )
        
        # Check cache
        cache_key = self.get_cache_key(action='generate', description=description, language=language)
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, "Returning cached code generation")
            return cached
        
        # Generate code
        generated_code = None
        explanation = None
        
        if self.ai_brain:
            # Use AI brain for generation
            prompt = self._build_generation_prompt(description, language, context)
            try:
                response = self.ai_brain.query(prompt)
                generated_code = self._extract_code_from_response(response)
                explanation = self._extract_explanation_from_response(response)
            except Exception as e:
                Logger.error(self.name, f"AI generation failed: {e}")
                return self.format_error(f"Code generation failed: {str(e)}", "AI_ERROR")
        else:
            # Use template-based generation as fallback
            generated_code = self._template_generation(description, language)
            explanation = f"Basic template for {description}"
        
        if not generated_code:
            return self.format_error("Failed to generate code", "GENERATION_FAILED")
        
        # Validate generated code
        validation = self._validate_code(generated_code, language)
        
        duration_ms = (time.time() - start_time) * 1000
        
        result_data = {
            'code': generated_code,
            'language': language,
            'explanation': explanation,
            'validation': validation,
            'lines': len(generated_code.split('\n')),
            'timestamp': datetime.now().isoformat(),
            'generation_time_ms': duration_ms
        }
        
        Logger.info(
            self.name,
            f"Generated {language} code",
            {'lines': result_data['lines'], 'time_ms': duration_ms}
        )
        
        # Cache result
        result = self.format_success(result_data, "Code generated successfully")
        self.cache_result(cache_key, result, ttl_minutes=60)
        
        return result
    
    def debug_code(self, code: str, error_message: str = None, language: str = None) -> Dict[str, Any]:
        """Debug code and suggest fixes.
        
        Args:
            code: Code with potential errors
            error_message: Optional error message from runtime
            language: Programming language (auto-detect if None)
            
        Returns:
            Debugging analysis with fix suggestions
        """
        start_time = time.time()
        
        if not code or not code.strip():
            return self.format_error("Code cannot be empty", "EMPTY_CODE")
        
        # Auto-detect language
        if not language:
            language = TextProcessor.detect_language(code)
        
        # Check cache
        cache_key = self.get_cache_key(action='debug', code=code, error=error_message, language=language)
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, "Returning cached debug analysis")
            return cached
        
        # Analyze code for errors
        analysis = self.analyze(code, language)
        
        if not analysis.get('success'):
            return analysis  # Return if analysis failed
        
        code_data = analysis.get('data', {})
        errors = code_data.get('errors', [])
        
        # Get AI-powered debugging suggestions
        suggestions = []
        fixed_code = None
        
        if self.ai_brain:
            try:
                debug_prompt = self._build_debug_prompt(code, error_message, language, errors)
                response = self.ai_brain.query(debug_prompt)
                suggestions = self._extract_suggestions_from_response(response)
                fixed_code = self._extract_code_from_response(response)
            except Exception as e:
                Logger.warning(self.name, f"AI debugging failed: {e}")
        
        # Fallback to static analysis suggestions
        if not suggestions:
            suggestions = self._static_debug_suggestions(code, errors, language)
        
        duration_ms = (time.time() - start_time) * 1000
        
        result_data = {
            'original_code': code,
            'language': language,
            'errors_found': errors,
            'error_message': error_message,
            'suggestions': suggestions,
            'fixed_code': fixed_code,
            'timestamp': datetime.now().isoformat(),
            'debug_time_ms': duration_ms
        }
        
        Logger.info(
            self.name,
            f"Debug analysis complete",
            {'errors': len(errors), 'suggestions': len(suggestions)}
        )
        
        # Cache result
        result = self.format_success(result_data, "Debugging analysis complete")
        self.cache_result(cache_key, result, ttl_minutes=30)
        
        return result
    
    def explain_code(self, code: str, language: str = None, detail_level: str = "medium") -> Dict[str, Any]:
        """Explain what code does in natural language.
        
        Args:
            code: Code to explain
            language: Programming language (auto-detect if None)
            detail_level: 'brief', 'medium', 'detailed'
            
        Returns:
            Code explanation with line-by-line breakdown
        """
        start_time = time.time()
        
        if not code or not code.strip():
            return self.format_error("Code cannot be empty", "EMPTY_CODE")
        
        # Auto-detect language
        if not language:
            language = TextProcessor.detect_language(code)
        
        # Check cache
        cache_key = self.get_cache_key(action='explain', code=code, language=language, detail=detail_level)
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, "Returning cached explanation")
            return cached
        
        explanation = {
            'language': language,
            'overview': '',
            'line_by_line': [],
            'key_concepts': [],
            'complexity': 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        if self.ai_brain:
            # Use AI for detailed explanation
            try:
                explain_prompt = self._build_explanation_prompt(code, language, detail_level)
                response = self.ai_brain.query(explain_prompt)
                explanation['overview'] = self._extract_overview_from_response(response)
                explanation['line_by_line'] = self._extract_line_explanations(response, code)
                explanation['key_concepts'] = self._extract_concepts(response)
            except Exception as e:
                Logger.warning(self.name, f"AI explanation failed: {e}")
                # Fallback to basic explanation
                explanation['overview'] = self._basic_explanation(code, language)
        else:
            # Basic explanation without AI
            explanation['overview'] = self._basic_explanation(code, language)
        
        # Add structural analysis
        if language == 'python':
            structure = self._analyze_python_structure(code)
            explanation['structure'] = structure
        
        duration_ms = (time.time() - start_time) * 1000
        
        Logger.info(self.name, f"Code explanation generated", {'language': language, 'time_ms': duration_ms})
        
        # Cache result
        result = self.format_success(explanation, "Code explanation generated")
        self.cache_result(cache_key, result, ttl_minutes=60)
        
        return result
    
    def refactor_code(self, code: str, language: str = None, goals: List[str] = None) -> Dict[str, Any]:
        """Suggest code refactoring improvements.
        
        Args:
            code: Code to refactor
            language: Programming language (auto-detect if None)
            goals: Refactoring goals (e.g., 'performance', 'readability', 'maintainability')
            
        Returns:
            Refactored code with improvement notes
        """
        start_time = time.time()
        
        if not code or not code.strip():
            return self.format_error("Code cannot be empty", "EMPTY_CODE")
        
        # Auto-detect language
        if not language:
            language = TextProcessor.detect_language(code)
        
        # Default goals
        if not goals:
            goals = ['readability', 'maintainability', 'performance']
        
        # Check cache
        cache_key = self.get_cache_key(action='refactor', code=code, language=language, goals=goals)
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, "Returning cached refactoring")
            return cached
        
        refactoring = {
            'original_code': code,
            'refactored_code': None,
            'improvements': [],
            'goals_addressed': goals,
            'language': language,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.ai_brain:
            # Use AI for intelligent refactoring
            try:
                refactor_prompt = self._build_refactor_prompt(code, language, goals)
                response = self.ai_brain.query(refactor_prompt)
                refactoring['refactored_code'] = self._extract_code_from_response(response)
                refactoring['improvements'] = self._extract_improvements_from_response(response)
            except Exception as e:
                Logger.warning(self.name, f"AI refactoring failed: {e}")
        
        # Apply static refactoring rules as fallback
        if not refactoring['refactored_code']:
            refactoring = self._apply_static_refactoring(code, language, goals)
        
        duration_ms = (time.time() - start_time) * 1000
        
        Logger.info(
            self.name,
            f"Refactoring suggestions generated",
            {'improvements': len(refactoring['improvements']), 'time_ms': duration_ms}
        )
        
        # Cache result
        result = self.format_success(refactoring, "Refactoring analysis complete")
        self.cache_result(cache_key, result, ttl_minutes=30)
        
        return result
    
    def generate_documentation(self, code: str, language: str = None, doc_format: str = "markdown") -> Dict[str, Any]:
        """Generate documentation for code.
        
        Args:
            code: Code to document
            language: Programming language (auto-detect if None)
            doc_format: 'markdown', 'rst', 'docstring'
            
        Returns:
            Generated documentation
        """
        start_time = time.time()
        
        if not code or not code.strip():
            return self.format_error("Code cannot be empty", "EMPTY_CODE")
        
        # Auto-detect language
        if not language:
            language = TextProcessor.detect_language(code)
        
        # Check cache
        cache_key = self.get_cache_key(action='document', code=code, language=language, format=doc_format)
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, "Returning cached documentation")
            return cached
        
        documentation = {
            'code': code,
            'language': language,
            'format': doc_format,
            'documentation': '',
            'sections': {},
            'timestamp': datetime.now().isoformat()
        }
        
        if self.ai_brain:
            # Use AI for comprehensive documentation
            try:
                doc_prompt = self._build_documentation_prompt(code, language, doc_format)
                response = self.ai_brain.query(doc_prompt)
                documentation['documentation'] = response
                documentation['sections'] = self._parse_documentation_sections(response)
            except Exception as e:
                Logger.warning(self.name, f"AI documentation failed: {e}")
        
        # Generate basic documentation as fallback
        if not documentation['documentation']:
            documentation = self._generate_basic_documentation(code, language, doc_format)
        
        duration_ms = (time.time() - start_time) * 1000
        
        Logger.info(self.name, f"Documentation generated", {'format': doc_format, 'time_ms': duration_ms})
        
        # Cache result
        result = self.format_success(documentation, "Documentation generated successfully")
        self.cache_result(cache_key, result, ttl_minutes=60)
        
        return result
    
    # ========== Python-specific Analysis ==========
    
    def _analyze_python(self, code: str) -> Dict[str, Any]:
        """Analyze Python code using AST."""
        analysis = {
            'syntax_valid': False,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'complexity': 'low',
            'functions': 0,
            'classes': 0
        }
        
        try:
            tree = ast.parse(code)
            analysis['syntax_valid'] = True
            
            # Count functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'] += 1
            
            # Complexity estimation
            if analysis['functions'] > 10 or analysis['classes'] > 5:
                analysis['complexity'] = 'high'
            elif analysis['functions'] > 5 or analysis['classes'] > 2:
                analysis['complexity'] = 'medium'
            
            # Static analysis checks
            analysis['warnings'].extend(self._check_python_style(code))
            
        except SyntaxError as e:
            analysis['syntax_valid'] = False
            analysis['errors'].append({
                'type': 'SyntaxError',
                'message': str(e),
                'line': e.lineno,
                'offset': e.offset
            })
        except Exception as e:
            analysis['errors'].append({
                'type': 'AnalysisError',
                'message': str(e)
            })
        
        return analysis
    
    def _analyze_python_structure(self, code: str) -> Dict[str, Any]:
        """Analyze Python code structure."""
        structure = {
            'imports': [],
            'functions': [],
            'classes': [],
            'global_vars': []
        }
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        structure['imports'].extend([alias.name for alias in node.names])
                    else:
                        structure['imports'].append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    structure['functions'].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    structure['classes'].append(node.name)
        except:
            pass
        
        return structure
    
    def _check_python_style(self, code: str) -> List[Dict]:
        """Check Python code style."""
        warnings = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                warnings.append({
                    'type': 'StyleWarning',
                    'message': 'Line exceeds 120 characters',
                    'line': i
                })
            
            # Check for bare except
            if 'except:' in line and 'except Exception' not in line:
                warnings.append({
                    'type': 'PracticeWarning',
                    'message': 'Bare except clause - specify exception type',
                    'line': i
                })
        
        return warnings
    
    # ========== JavaScript Analysis ==========
    
    def _analyze_javascript(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code."""
        analysis = {
            'syntax_valid': True,  # Basic check
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'complexity': 'medium',
            'functions': 0,
            'arrow_functions': 0
        }
        
        # Count functions
        function_patterns = [
            r'function\s+\w+',  # function declarations
            r'\w+\s*:\s*function',  # object methods
            r'=>',  # arrow functions
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, code)
            if pattern == r'=>':
                analysis['arrow_functions'] = len(matches)
            else:
                analysis['functions'] += len(matches)
        
        # Check for common issues
        if 'var ' in code:
            analysis['warnings'].append({
                'type': 'ModernJSWarning',
                'message': 'Consider using let or const instead of var'
            })
        
        if '==' in code and '===' not in code:
            analysis['warnings'].append({
                'type': 'ComparisonWarning',
                'message': 'Consider using === for strict equality'
            })
        
        return analysis
    
    # ========== Generic Analysis ==========
    
    def _analyze_generic(self, code: str) -> Dict[str, Any]:
        """Generic code analysis for unsupported languages."""
        analysis = {
            'syntax_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': ['Language-specific analysis not available'],
            'complexity': 'unknown'
        }
        
        lines = code.split('\n')
        
        # Basic metrics
        comment_lines = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*')))
        blank_lines = sum(1 for line in lines if not line.strip())
        code_lines = len(lines) - comment_lines - blank_lines
        
        analysis['metrics'] = {
            'total_lines': len(lines),
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines
        }
        
        return analysis
    
    # ========== AI Integration ==========
    
    def _get_ai_analysis(self, code: str, language: str) -> str:
        """Get AI-powered code analysis."""
        prompt = f"""Analyze this {language} code and provide insights:

```{language}
{code}
```

Provide:
1. Code quality assessment
2. Potential issues or improvements
3. Best practices recommendations

Keep it concise."""
        
        try:
            return self.ai_brain.query(prompt)
        except Exception as e:
            Logger.warning(self.name, f"AI analysis failed: {e}")
            return None
    
    def _build_generation_prompt(self, description: str, language: str, context: str = None) -> str:
        """Build prompt for code generation."""
        prompt = f"""Generate {language} code for the following requirement:

{description}"""
        
        if context:
            prompt += f"\n\nContext/Existing code:\n```{language}\n{context}\n```"
        
        prompt += f"""

Provide:
1. Clean, working {language} code
2. Brief explanation of the implementation
3. Any assumptions made

Format:
```{language}
[code here]
```

Explanation: [explanation here]"""
        
        return prompt
    
    def _build_debug_prompt(self, code: str, error_message: str, language: str, errors: List) -> str:
        """Build prompt for debugging."""
        prompt = f"""Debug this {language} code:

```{language}
{code}
```"""
        
        if error_message:
            prompt += f"\n\nError message:\n{error_message}"
        
        if errors:
            prompt += f"\n\nStatic analysis found {len(errors)} issues."
        
        prompt += """

Provide:
1. Identified problems
2. Fixed code
3. Explanation of what was wrong"""
        
        return prompt
    
    def _build_explanation_prompt(self, code: str, language: str, detail_level: str) -> str:
        """Build prompt for code explanation."""
        prompt = f"""Explain this {language} code at {detail_level} detail level:

```{language}
{code}
```

Provide:
1. Overview of what the code does
2. Key concepts and algorithms used
"""
        
        if detail_level in ['medium', 'detailed']:
            prompt += "3. Line-by-line explanation for complex sections\n"
        
        if detail_level == 'detailed':
            prompt += "4. Performance considerations\n5. Possible improvements"
        
        return prompt
    
    def _build_refactor_prompt(self, code: str, language: str, goals: List[str]) -> str:
        """Build prompt for refactoring."""
        goals_str = ', '.join(goals)
        return f"""Refactor this {language} code focusing on: {goals_str}

```{language}
{code}
```

Provide:
1. Refactored code
2. List of improvements made
3. Why each change improves the code"""
    
    def _build_documentation_prompt(self, code: str, language: str, doc_format: str) -> str:
        """Build prompt for documentation."""
        return f"""Generate {doc_format} documentation for this {language} code:

```{language}
{code}
```

Include:
1. Overview/Purpose
2. Parameters/Arguments
3. Return values
4. Usage examples
5. Notes/Warnings if applicable"""
    
    # ========== Response Parsing ==========
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract code block from AI response."""
        # Try to find code in markdown blocks
        code_blocks = TextProcessor.extract_code_blocks(response)
        if code_blocks and code_blocks[0]:
            return code_blocks[0].strip()
        
        # If no code blocks, return the response itself if it looks like code
        if any(char in response for char in ['{', '}', '(', ')', ';', 'def ', 'function']):
            return response.strip()
        
        return None
    
    def _extract_explanation_from_response(self, response: str) -> str:
        """Extract explanation from AI response."""
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', response)
        # Look for explanation markers
        if 'Explanation:' in text:
            return text.split('Explanation:')[1].strip()
        return text.strip()
    
    def _extract_suggestions_from_response(self, response: str) -> List[str]:
        """Extract suggestions from debugging response."""
        suggestions = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '-', '*', '•')):
                suggestions.append(line.lstrip('0123456789.-*• '))
        return suggestions if suggestions else [response]
    
    def _extract_improvements_from_response(self, response: str) -> List[Dict]:
        """Extract improvements from refactoring response."""
        improvements = []
        lines = response.split('\n')
        current_improvement = None
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '-', '*')):
                if current_improvement:
                    improvements.append(current_improvement)
                current_improvement = {'description': line.lstrip('0123456789.-* ')}
            elif current_improvement and line:
                current_improvement['reason'] = line
        
        if current_improvement:
            improvements.append(current_improvement)
        
        return improvements if improvements else [{'description': response}]
    
    def _extract_overview_from_response(self, response: str) -> str:
        """Extract overview from explanation response."""
        lines = response.split('\n')
        overview_lines = []
        for line in lines:
            if line.strip() and not line.strip().startswith('```'):
                overview_lines.append(line.strip())
                if len(overview_lines) >= 3:  # First few lines
                    break
        return ' '.join(overview_lines)
    
    def _extract_line_explanations(self, response: str, code: str) -> List[Dict]:
        """Extract line-by-line explanations."""
        # This would need more sophisticated parsing in production
        return []
    
    def _extract_concepts(self, response: str) -> List[str]:
        """Extract key concepts from explanation."""
        concepts = []
        keywords = ['algorithm', 'pattern', 'function', 'class', 'module', 'api', 'database']
        for keyword in keywords:
            if keyword in response.lower():
                concepts.append(keyword.capitalize())
        return concepts
    
    def _parse_documentation_sections(self, doc: str) -> Dict[str, str]:
        """Parse documentation into sections."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in doc.split('\n'):
            if line.startswith('#'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    # ========== Fallback Methods ==========
    
    def _validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate generated code."""
        validation = {
            'valid': True,
            'syntax_errors': [],
            'warnings': []
        }
        
        if language == 'python':
            try:
                ast.parse(code)
            except SyntaxError as e:
                validation['valid'] = False
                validation['syntax_errors'].append(str(e))
        
        return validation
    
    def _template_generation(self, description: str, language: str) -> str:
        """Generate code using templates (fallback)."""
        if language == 'python':
            return f'''def solution():
    """
    {description}
    """
    # TODO: Implement functionality
    pass

if __name__ == "__main__":
    solution()'''
        
        elif language == 'javascript':
            return f'''function solution() {{
    // {description}
    // TODO: Implement functionality
}}

solution();'''
        
        else:
            return f"// {description}\n// TODO: Implement in {language}"
    
    def _basic_explanation(self, code: str, language: str) -> str:
        """Generate basic explanation without AI."""
        lines = len(code.split('\n'))
        return f"This is a {language} code snippet with {lines} lines. It contains various programming constructs and logic."
    
    def _static_debug_suggestions(self, code: str, errors: List, language: str) -> List[str]:
        """Generate debugging suggestions from static analysis."""
        suggestions = []
        
        if errors:
            suggestions.append(f"Found {len(errors)} syntax/analysis errors")
            for error in errors[:3]:  # Limit to top 3
                suggestions.append(f"Fix {error.get('type', 'error')}: {error.get('message', 'Unknown')}")
        else:
            suggestions.append("No obvious errors detected. Code appears syntactically correct.")
            suggestions.append("Consider checking runtime behavior and edge cases.")
        
        return suggestions
    
    def _apply_static_refactoring(self, code: str, language: str, goals: List[str]) -> Dict[str, Any]:
        """Apply basic refactoring rules."""
        refactored = code
        improvements = []
        
        if 'readability' in goals:
            # Basic formatting improvements
            if language == 'python':
                # Ensure consistent indentation (simple version)
                lines = code.split('\n')
                improvements.append({
                    'description': 'Code formatting improved',
                    'reason': 'Better readability'
                })
        
        return {
            'original_code': code,
            'refactored_code': refactored,
            'improvements': improvements if improvements else [
                {'description': 'No automatic refactoring available', 
                 'reason': 'AI brain required for intelligent refactoring'}
            ],
            'goals_addressed': goals,
            'language': language,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_basic_documentation(self, code: str, language: str, doc_format: str) -> Dict[str, Any]:
        """Generate basic documentation without AI."""
        lines = code.split('\n')
        non_empty = [l for l in lines if l.strip()]
        
        if doc_format == 'markdown':
            doc = f"""# {language.capitalize()} Code Documentation

## Overview
This code contains {len(non_empty)} lines of {language} code.

## Structure
- Total lines: {len(lines)}
- Code lines: {len(non_empty)}

## Usage
Refer to inline comments and function signatures for usage details.
"""
        else:
            doc = f"{language.capitalize()} code with {len(non_empty)} lines."
        
        return {
            'code': code,
            'language': language,
            'format': doc_format,
            'documentation': doc,
            'sections': {'Overview': f'{len(non_empty)} lines of code'},
            'timestamp': datetime.now().isoformat()
        }
