# Frontend Patterns (Quick Reference)

Essential patterns for frontend work in BudTags.

---

## ⚠️ MANDATORY: Use Existing Components

**NEVER create new components for these - they already exist:**

| Need | Use This File | Components |
|------|---------------|------------|
| Buttons | `Components/Button.tsx` | `<Button>`, `<Button primary>` |
| Text inputs | `Components/Inputs.tsx` | `<TextInput>` |
| Textareas | `Components/Inputs.tsx` | `<TextArea>` |
| Selects | `Components/Inputs.tsx` | `<Select>` |
| Checkboxes | `Components/Inputs.tsx` | `<Checkbox>` |
| Toggles | `Components/ToggleSwitch.tsx` | `<ToggleSwitch>` |
| Tables | `Components/DataTable.tsx` | `<DataTable>` |
| Badges | `Components/Badge.tsx` | `<Badge>` |
| Searchable dropdowns | `Components/FuzzyPicker.tsx` | `<FuzzyPicker>` |
| Date pickers | `Components/DateRangePicker.tsx` | `<DateRangePicker>` |
| Alerts/warnings | `Components/WarningBox.tsx` | `<WarningBox>` |
| Content boxes | `Components/BoxMain.tsx` | `<BoxMain>` |
| Section headers | `Components/Headline.tsx` | `<Headline>` |

**Before creating ANY component:**
1. Glob `resources/js/Components/**/*.tsx`
2. READ existing components to understand props/usage
3. If it exists, USE IT. If not, document why in "Decisions Made"

---

## Page Pattern

```tsx
interface Props {
    items: FeatureItem[];
}

export default function Index({ items }: Props) {
    return (
        <AuthenticatedLayout>
            <Head title="Features" />
            <div className="py-12">
                {/* content */}
            </div>
        </AuthenticatedLayout>
    );
}
```

## Form Pattern (Inertia useForm) - MANDATORY

**ALL forms MUST use Inertia's `useForm` hook. No exceptions.**

### Basic Form
```tsx
import { useForm } from '@inertiajs/react';

const { data, setData, post, processing, errors, reset } = useForm({
    name: '',
    description: '',
});

const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    post(route('features-store'), {
        onSuccess: () => { reset(); onClose(); },
    });
};
```

### Form with Different HTTP Methods
```tsx
// Create (POST)
post(route('items-create'), { onSuccess: () => onClose() });

// Update (PUT)
put(route('items-update', item.id), { onSuccess: () => onClose() });

// Delete (DELETE)
delete_(route('items-delete', item.id), { onSuccess: () => onClose() });

// Note: delete is aliased as delete_ because delete is a reserved word
```

### Input Binding Pattern
```tsx
<TextInput
    label="Name"
    value={data.name}
    onChange={(e) => setData('name', e.target.value)}
    error={errors.name}
    required
/>

<Select
    label="Category"
    value={data.category_id}
    onChange={(e) => setData('category_id', e.target.value)}
    error={errors.category_id}
    options={categories.map(c => ({ value: c.id, label: c.name }))}
/>

<ToggleSwitch
    label="Active"
    checked={data.is_active}
    onChange={(checked) => setData('is_active', checked)}
/>
```

### Error Display
```tsx
// Errors come from useForm automatically from Laravel validation
{errors.name && <InputError message={errors.name} />}

// Or use the error prop on input components
<TextInput error={errors.name} />
```

### ⛔ FORBIDDEN - Never Do These

```tsx
// ❌ WRONG - Don't use useState for form fields
const [name, setName] = useState('');

// ❌ WRONG - Don't use axios/fetch for mutations
axios.post('/api/items', data);
fetch('/api/items', { method: 'POST', body: JSON.stringify(data) });

// ❌ WRONG - Don't use react-hook-form
const { register, handleSubmit } = useForm();

// ❌ WRONG - Don't lift form state to parent
<Modal formData={formData} setFormData={setFormData} />

// ❌ WRONG - Don't manage errors manually
const [errors, setErrors] = useState({});
```

### ✅ CORRECT - Modal Owns Its Form
```tsx
// Modal component is self-contained
export const CreateItemModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
    isOpen, onClose
}) => {
    // Form state lives INSIDE the modal, not passed from parent
    const { data, setData, post, processing, errors, reset } = useForm({
        name: '',
    });

    // ...
};

// Parent just controls open/close
const [isModalOpen, setIsModalOpen] = useState(false);
<CreateItemModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
```

## Button Pattern

```tsx
// ✅ CORRECT
<Button primary disabled={processing}>Save</Button>
<Button onClick={onClose}>Cancel</Button>

// ❌ WRONG - never use type attribute
<Button type="submit">Save</Button>
```

## Modal Pattern (Self-Contained)

```tsx
export const CreateModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
    isOpen, onClose
}) => {
    const { data, setData, post, processing, reset } = useForm({ name: '' });
    // Modal owns its form state - not the parent
};
```

## Critical Rules

- **No `type` attribute** on Button components
- **No `any`** in TypeScript - define proper interfaces
- **Self-contained modals** - modal owns its form state
- **MainLayout handles flash** - don't manually show toasts for redirects
- Use **Inertia** for forms/CRUD, **React Query** for polling/real-time
