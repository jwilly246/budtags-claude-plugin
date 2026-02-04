# Scenario: React Component

**Use this checklist when verifying React components.**

---

## Required Pattern Files

- `patterns/frontend-critical.md` - Component patterns
- `patterns/frontend-typescript.md` - Type safety
- IF data fetching: `patterns/frontend-data-fetching.md`
- IF forms: `patterns/backend-flash-messages.md`

---

## Component Structure Checklist

### TypeScript Types
- [ ] Interface defined for all component props
- [ ] NO `any` type usage
- [ ] Explicit types for all function parameters
- [ ] Explicit return types for functions
- [ ] Uses types from `types.tsx` or `types-metrc.tsx`

### Modal Components (if applicable)
- [ ] Self-contained (handles own form state and submission)
- [ ] Uses `useForm` hook (not multiple `useState`)
- [ ] Uses `useModalState` hook
- [ ] Pre-fills smart defaults in `useEffect`
- [ ] Only depends on `isOpen` in useEffect, not functions
- [ ] Handles `onSuccess` and `onError`
- [ ] Only closes modal AFTER successful submission

### Error Handling & Confirmations
- [ ] Uses `toast.error()` (NEVER `alert()` or `confirm()`)
- [ ] Uses modal for confirmations (NEVER `confirm()` or `window.confirm()`)
- [ ] Typed toast methods (`toast.error`, `toast.success`, etc.)
- [ ] Client-side validation before submit
- [ ] onError callback handles validation errors

### Data Flow
- [ ] Verified data source in `HandleInertiaRequests`
- [ ] NO assumptions about `window` globals
- [ ] Correct access methods (`.some()` for object arrays, not `.includes()`)
- [ ] Uses `usePage<PageProps>().props` for shared data

### Form Handling
- [ ] Uses `useForm` from `@inertiajs/react`
- [ ] Uses reusable input components (`InputSelect`, `InputDate`, etc.)
- [ ] NO raw HTML inputs (`<input>`, `<select>`)
- [ ] Error messages displayed from `errors` object

### Performance & React Compiler
- [ ] Aware that React 19.2 + React Compiler auto-memoizes most cases
- [ ] Only uses `useMemo` for genuinely expensive computations (100ms+)
- [ ] Uses `'use no-forget'` directive if component has compiler issues
- [ ] No console.log() statements (remove before committing)

---

## Common Violations

### Using `any`
```typescript
// ❌ WRONG
const MyComponent = (props: any) => { ... }

// ✅ FIX
interface MyComponentProps {
    items: Item[];
    onSelect: (id: number) => void;
}
const MyComponent: React.FC<MyComponentProps> = ({ items, onSelect }) => { ... }
```

### Using alert() or confirm()
```typescript
// ❌ WRONG - Never use browser dialogs
alert('Please select an item');
confirm('Are you sure?');
window.confirm('Delete this item?');

// ✅ FIX - Use toast for messages
toast.error('Please select an item');

// ✅ FIX - Use modal for confirmations
const [showConfirm, setShowConfirm] = useState(false);
// ... modal component with confirm/cancel buttons
```

### Assuming Data Exists
```typescript
// ❌ WRONG
{window.Laravel.features.includes('dev-features') && <Button />}

// ✅ FIX
const { user } = usePage<PageProps>().props;
{user?.active_org?.features?.some(f => f.name === 'dev-features') && <Button />}
```

---

## Example: Compliant Modal Component

```typescript
import { useForm } from '@inertiajs/react';
import { useModalState } from '@/Hooks/useModalState';
import { toast } from 'react-toastify';

interface MyModalProps {
    isOpen: boolean;
    onClose: () => void;
    items: Item[];
}

const MyModal: React.FC<MyModalProps> = ({ isOpen, onClose, items }) => {
    const { cancelButtonRef, getTodayDate } = useModalState(isOpen);
    const { data, setData, post, processing, errors } = useForm({
        name: '',
        quantity: 0,
    });

    useEffect(() => {
        if (isOpen) {
            setData('name', getTodayDate());
        }
    }, [isOpen]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (!data.name) {
            toast.error('Name is required');
            return;
        }

        post('/api/endpoint', {
            onSuccess: () => {
                onClose();
            },
            onError: (errors) => {
                toast.error(Object.values(errors)[0] as string);
            }
        });
    };

    return (
        <Modal show={isOpen} onClose={onClose}>
            <form onSubmit={handleSubmit}>
                <InputText
                    value={data.name}
                    onChange={(e) => setData('name', e.target.value)}
                    errors={errors.name}
                />
                <Button ref={cancelButtonRef}>Cancel</Button>
                <Button primary disabled={processing}>Save</Button>
            </form>
        </Modal>
    );
};
```
