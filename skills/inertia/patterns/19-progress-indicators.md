# Pattern 19: Progress Indicators

## Built-in Progress Bar

Inertia includes a built-in progress indicator using NProgress.

### Configuration

```tsx
// app.tsx
createInertiaApp({
  // ...
  progress: {
    color: '#4B5563',     // Progress bar color
    showSpinner: false,   // Hide loading spinner (default: false)
    delay: 250,           // Delay before showing (ms, default: 250)
  },
});
```

### BudTags Configuration

```tsx
createInertiaApp({
  // ...
  progress: {
    color: '#F87415',  // Orange brand color
  },
});
```

---

## Disable Progress Bar

```tsx
createInertiaApp({
  // ...
  progress: false,  // Disable completely
});
```

---

## Custom Progress Indicator

### Global Loading State

```tsx
import { router } from '@inertiajs/react';
import { useState, useEffect } from 'react';

function GlobalLoader() {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const startListener = router.on('start', () => setLoading(true));
    const finishListener = router.on('finish', () => setLoading(false));

    return () => {
      startListener();
      finishListener();
    };
  }, []);

  if (!loading) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-50">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent" />
    </div>
  );
}
```

### Top Loading Bar (Custom)

```tsx
function TopLoadingBar() {
  const [progress, setProgress] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const start = router.on('start', () => {
      setVisible(true);
      setProgress(0);
      interval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 100);
    });

    const finish = router.on('finish', () => {
      clearInterval(interval);
      setProgress(100);
      setTimeout(() => {
        setVisible(false);
        setProgress(0);
      }, 200);
    });

    return () => {
      start();
      finish();
      clearInterval(interval);
    };
  }, []);

  if (!visible) return null;

  return (
    <div
      className="fixed top-0 left-0 h-1 bg-blue-600 transition-all duration-200 z-50"
      style={{ width: `${progress}%` }}
    />
  );
}
```

---

## Per-Request Progress

### Form Submission Loading

```tsx
const { processing } = useForm({ name: '' });

<button disabled={processing}>
  {processing ? (
    <>
      <Spinner className="w-4 h-4 mr-2" />
      Saving...
    </>
  ) : (
    'Save'
  )}
</button>
```

### Manual Visit Loading

```tsx
function RefreshButton() {
  const [loading, setLoading] = useState(false);

  const handleRefresh = () => {
    router.reload({
      onStart: () => setLoading(true),
      onFinish: () => setLoading(false),
    });
  };

  return (
    <button onClick={handleRefresh} disabled={loading}>
      {loading ? 'Refreshing...' : 'Refresh'}
    </button>
  );
}
```

---

## File Upload Progress

```tsx
const { progress, post } = useForm({ file: null });

<input type="file" onChange={e => setData('file', e.target.files[0])} />

{progress && (
  <div className="mt-2">
    <div className="bg-gray-200 rounded h-2">
      <div
        className="bg-blue-600 h-2 rounded transition-all"
        style={{ width: `${progress.percentage}%` }}
      />
    </div>
    <span className="text-sm text-gray-600">
      {progress.percentage}% uploaded
    </span>
  </div>
)}
```

---

## NProgress Customization

Add custom CSS for NProgress:

```css
/* In your CSS file */
#nprogress {
  pointer-events: none;
}

#nprogress .bar {
  background: #F87415;
  position: fixed;
  z-index: 1031;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
}

#nprogress .peg {
  display: block;
  position: absolute;
  right: 0px;
  width: 100px;
  height: 100%;
  box-shadow: 0 0 10px #F87415, 0 0 5px #F87415;
  opacity: 1.0;
  transform: rotate(3deg) translate(0px, -4px);
}
```

---

## Loading Skeletons

Show content placeholders while loading:

```tsx
function PackagesSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="flex items-center space-x-4">
          <div className="h-4 w-32 bg-gray-200 rounded" />
          <div className="h-4 w-24 bg-gray-200 rounded" />
          <div className="h-4 w-48 bg-gray-200 rounded" />
        </div>
      ))}
    </div>
  );
}
```

---

## Next Steps

- **Remembering State** → Read `20-remembering-state.md`
- **Events** → Read `21-events-lifecycle.md`
