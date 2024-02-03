<script lang="ts">
    export let value: number;
    export let label: string;
</script>

<div class="bg-primary/20 flex flex-col items-center rounded-lg w-14 h-14 p-1.5">
    <div class="leading-[1.2] text-2xl">
        {`${value}`.padStart(2, '0')}
    </div>
    <div class="border-t border-t-neutral/20 leading-[1.6] text-[11px] text-neutral/80">
        {label}
    </div>
</div>