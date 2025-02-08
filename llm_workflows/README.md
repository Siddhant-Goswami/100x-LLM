# Marketing Copy Generator using Prompt Chaining Workflow

A Python implementation demonstrating how to build sequential AI operations (prompt chains) using Groq API. This implementation shows a practical workflow for generating, reviewing, and translating marketing content through a series of connected prompts.

## 📊 Prompt Chain Architecture

```
┌──────────────────────────────────────────────────────────┐
│ PROMPT TEMPLATES                                         │
├──────────────────────────────────────────────────────────┤
│ GENERATE_TEMPLATE   │ REVIEW_TEMPLATE   │ TRANSLATE_TEMPLATE │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│ WORKFLOW EXECUTION FLOW                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Input → Generate → Review → Translate → Final Output    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 🔍 Implementation Details

### 1. Prompt Templates

Each step in the workflow uses a carefully crafted prompt template:

#### Generate Template
```python
GENERATE_TEMPLATE = """
Create compelling marketing copy for the following product:
Product: {product}
Target Audience: {target_audience}
...
"""
```
- Variables: `product`, `target_audience`
- Purpose: Creates initial marketing content

#### Review Template
```python
REVIEW_TEMPLATE = """
Review and improve the following marketing copy:
Copy: {marketing_copy}
...
"""
```
- Variables: `marketing_copy`
- Purpose: Enhances and polishes the content

#### Translate Template
```python
TRANSLATE_TEMPLATE = """
Translate the following marketing copy to {target_language}:
Copy: {reviewed_copy}
...
"""
```
- Variables: `reviewed_copy`, `target_language`
- Purpose: Provides culturally-appropriate translation

### 2. Workflow Execution

The prompt chain executes in the following sequence:

```python
def generate_marketing_content(product, target_audience, target_language):
    # Step 1: Generate
    marketing_copy = get_completion(GENERATE_TEMPLATE.format(...))
    
    # Step 2: Review
    reviewed_copy = get_completion(REVIEW_TEMPLATE.format(...))
    
    # Step 3: Translate
    translated_copy = get_completion(TRANSLATE_TEMPLATE.format(...))
```

## 🔄 Data Flow Details

### Input Stage
```python
{
    "product": str,          # Product description
    "target_audience": str,  # Target market description
    "target_language": str   # Desired translation language
}
```

### Intermediate Stages
1. **Generation Stage**
   - Input: Product + Audience
   - Output: Raw marketing copy
   
2. **Review Stage**
   - Input: Raw marketing copy
   - Output: Polished marketing copy
   
3. **Translation Stage**
   - Input: Polished copy + Target language
   - Output: Translated marketing copy

### Output Stage
```python
{
    "marketing_copy": str,    # Initial generated copy
    "reviewed_copy": str,     # Improved version
    "translated_copy": str    # Final translated version
}
```

## 🛠 Technical Components

1. **API Integration**
   ```python
   client = Groq(api_key=os.getenv("GROQ_API_KEY"))
   ```

2. **Completion Function**
   ```python
   def get_completion(prompt: str) -> str:
       return client.chat.completions.create(
           model="llama3-8b-8192",
           messages=[{"role": "user", "content": prompt}]
       ).choices[0].message.content
   ```

## 📝 Usage Example

```python
# Initialize with product details
result = generate_marketing_content(
    product="Smart Fitness Watch",
    target_audience="Health-conscious young professionals",
    target_language="Spanish"
)

# Access results
print(result["marketing_copy"])     # Initial copy
print(result["reviewed_copy"])      # Improved copy
print(result["translated_copy"])    # Spanish translation
```

## 🔧 Customization Points

1. **Modify Prompt Templates**
   - Adjust the prompts in `GENERATE_TEMPLATE`, `REVIEW_TEMPLATE`, or `TRANSLATE_TEMPLATE`
   - Add specific requirements or constraints to each step

2. **Add New Chain Steps**
   - Create new prompt templates
   - Extend the `generate_marketing_content` function
   - Add new output types to the result dictionary

3. **Change Model Parameters**
   - Modify the model name in `get_completion`
   - Adjust temperature or other parameters for different creativity levels

## 🚀 Advanced Usage

### Adding Error Handling
```python
try:
    result = generate_marketing_content(...)
except Exception as e:
    print(f"Error in workflow execution: {e}")
```

### Progress Tracking
The implementation includes progress printing:
```python
print("Step 1: Generating initial marketing copy...")
print("Step 2: Reviewing and improving the copy...")
print("Step 3: Translating the improved copy...")
```

## 📊 Performance Considerations

1. **API Calls**: Each step makes one API call
2. **Sequential Processing**: Steps run in sequence, not parallel
3. **Memory Usage**: Minimal, only stores current state
4. **Response Time**: Depends on API response times

## 🔍 Debugging Tips

1. Print intermediate results:
   ```python
   print(f"After generation: {marketing_copy}")
   print(f"After review: {reviewed_copy}")
   ```

2. Check prompt formatting:
   ```python
   print(f"Generated prompt: {generate_prompt}")
   ```

3. Monitor API responses:
   ```python
   print(f"API response: {completion}")
   ``` 